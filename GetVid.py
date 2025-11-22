"""
Script to download video content from Reddit.
"""
import praw
import os
import yt_dlp  # More reliable than youtube-dl
from prawcore.exceptions import Redirect, NotFound, Forbidden
import logging
from pathlib import Path

import config
import utils

# Set up logger
logger = logging.getLogger(__name__)

def download_media(url: str, title: str, submission_id: str) -> bool:
    """
    Download the video using yt-dlp only if it meets the criteria (duration <= 120 sec).
    
    Args:
        url: URL of the media to download
        title: Title to use for the downloaded file
        submission_id: Reddit submission ID for tracking
        
    Returns:
        True if download was successful, otherwise False
    """
    sanitized_title = utils.sanitize_filename(title)
    
    # Define a filter to skip videos longer than MAX_VIDEO_DURATION seconds
    def duration_filter(info):
        duration = info.get('duration')
        if duration and duration > config.MAX_VIDEO_DURATION:
            return f"Video duration exceeds {config.MAX_VIDEO_DURATION} seconds."
        return None

    # yt-dlp options for merging video and audio
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{sanitized_title}.%(ext)s',
        'ffmpeg_location': config.FFMPEG_PATH,
        'quiet': True,
        'no_warnings': True,
        'match_filter': duration_filter,  # Apply the duration filter
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logger.info(f"Successfully downloaded: {title}")
        
        # Append the video title to VidTitle.txt
        utils.write_file_content(config.VID_TITLE_FILE, title)
        return True
    except Exception as e:
        logger.error(f"Failed to download {title}: {str(e)}")
        return False

def check_new_videos() -> bool:
    """
    Check for and download videos from selected subreddits.
    Stops immediately after finding and downloading the first new video.
    
    Returns:
        True if a video was successfully downloaded, otherwise False
    """
    # Load the IDs of videos that have already been downloaded
    downloaded_ids = set()
    if config.DOWNLOADED_IDS_FILE.exists():
        downloaded_ids = set(utils.read_file_content(config.DOWNLOADED_IDS_FILE).splitlines())

    # Read subreddit names from the subreddit list file
    subreddit_content = utils.read_file_content(config.SUBREDDIT_LIST_FILE)
    if not subreddit_content:
        logger.error(f"Error: Subreddit list is empty or file does not exist: {config.SUBREDDIT_LIST_FILE}")
        return False
    
    subreddit_names = [line.strip() for line in subreddit_content.splitlines() if line.strip()]
    
    # Initialize Reddit instance
    try:
        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT
        )
    except Exception as e:
        logger.error(f"Failed to initialize Reddit API: {str(e)}")
        return False

    # Process each subreddit in order until a video is successfully downloaded
    for subreddit_name in subreddit_names:
        logger.info(f"Processing subreddit: {subreddit_name}")
        try:
            subreddit = reddit.subreddit(subreddit_name)
            # Verify subreddit exists by accessing its id
            _ = subreddit.id
        except NotFound:
            logger.warning(f"Error: Subreddit '{subreddit_name}' does not exist")
            continue
        except Redirect:
            logger.warning(f"Error: Subreddit '{subreddit_name}' is invalid")
            continue
        except Forbidden:
            logger.warning(f"Error: Access to subreddit '{subreddit_name}' is forbidden")
            continue
        except Exception as e:
            logger.warning(f"Error accessing subreddit '{subreddit_name}': {str(e)}")
            continue

        try:
            # Check the top submission from today; adjust the limit as needed
            for submission in subreddit.top(time_filter="day", limit=1):
                # Skip NSFW posts
                if submission.over_18:
                    logger.info(f"Skipping NSFW post: {submission.title}")
                    continue

                # Skip if this submission has already been processed
                if submission.id in downloaded_ids:
                    logger.info(f"Skipping already downloaded video: {submission.title}")
                    continue

                # Process Reddit-hosted videos
                if submission.is_video:
                    video_url = submission.media['reddit_video']['fallback_url']
                    # Remove DASH suffix if present
                    if "v.redd.it" in video_url:
                        parts = video_url.split('/')
                        if len(parts) >= 4:
                            video_url = f"https://v.redd.it/{parts[3]}"
                    
                    success = download_media(video_url, submission.title, submission.id)
                    if success:
                        # Record submission ID to avoid future downloads
                        utils.append_to_file(config.DOWNLOADED_IDS_FILE, f"{submission.id}\n")
                        downloaded_ids.add(submission.id)
                        # Stop processing further subreddits once a video is downloaded
                        return True
                    else:
                        continue

                # Process external video links (e.g., YouTube)
                if submission.url and any(ext in submission.url for ext in ['youtube.com', 'youtu.be', 'v.redd.it']):
                    success = download_media(submission.url, submission.title, submission.id)
                    if success:
                        utils.append_to_file(config.DOWNLOADED_IDS_FILE, f"{submission.id}\n")
                        downloaded_ids.add(submission.id)
                        # Stop processing further subreddits once a video is downloaded
                        return True
        except Exception as e:
            logger.error(f"Error fetching posts from {subreddit_name}: {str(e)}")
    
    logger.info("No new suitable videos found across all subreddits.")
    return False

if __name__ == '__main__':
    check_new_videos()
