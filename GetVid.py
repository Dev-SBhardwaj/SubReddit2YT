import praw
import os
import yt_dlp  # More reliable than youtube-dl
from prawcore.exceptions import Redirect, NotFound, Forbidden
import re

# Reddit API credentials
client_id = 'ENTER YOUR CLIENT ID HERE'
client_secret = 'ENTER YOUR CLIENT SECRET HERE'
user_agent = 'VideoDownloader/1.0 (by /u/ENTER_YOUR_REDDIT_USERNAME_HERE)'  # Update with your username

# Subreddit to monitor
subreddit_name = 'ENTER_YOUR_SUBREDDIT_HERE'

# Directory to save downloaded videos
download_dir = r'ENTER YOUR PATH HERE'
os.makedirs(download_dir, exist_ok=True)

# Path for the video title file and downloaded IDs file
vid_title_file = os.path.join(download_dir, "VidTitle.txt")
downloaded_ids_file = os.path.join(download_dir, "downloaded_ids.txt")

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

def sanitize_filename(title):
    """Remove invalid characters from filenames and truncate long titles."""
    return re.sub(r'[\\/*?:"<>|]', '', title)[:50]

def download_media(url, title, submission_id):
    """
    Download the video using yt-dlp only if it meets the criteria (duration <= 120 sec).
    Returns True if download was successful, otherwise False.
    """
    sanitized_title = sanitize_filename(title)
    
    # Define a filter to skip videos longer than 120 seconds (2 minutes)
    def duration_filter(info):
        duration = info.get('duration')
        if duration and duration > 120:
            return "Video duration exceeds 120 seconds."
        return None

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(download_dir, f'{sanitized_title}.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'match_filter': duration_filter,  # Apply the duration filter
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Successfully downloaded: {title}")
        # Append the video title to VidTitle.txt
        with open(vid_title_file, "a", encoding="utf-8") as f:
            f.write(title + "\n")
        return True
    except Exception as e:
        print(f"Failed to download {title}: {str(e)}")
        return False

def check_new_videos():
    # Load the IDs of videos that have already been downloaded
    downloaded_ids = set()
    if os.path.exists(downloaded_ids_file):
        with open(downloaded_ids_file, "r", encoding="utf-8") as f:
            for line in f:
                downloaded_ids.add(line.strip())

    try:
        subreddit = reddit.subreddit(subreddit_name)
        # Verify subreddit exists by accessing its id
        subreddit.id
    except NotFound:
        print(f"Error: Subreddit '{subreddit_name}' does not exist")
        return
    except Redirect:
        print(f"Error: Subreddit '{subreddit_name}' is invalid")
        return
    except Forbidden:
        print(f"Error: Access to subreddit '{subreddit_name}' is forbidden")
        return

    try:
        # Check the newest submissions; adjust the limit as needed
        for submission in subreddit.new(limit=1):
            # Skip if the post is marked as NSFW
            if submission.over_18:
                continue

            # Skip if this submission has been processed before
            if submission.id in downloaded_ids:
                print(f"Skipping already downloaded video: {submission.title}")
                continue

            # Check for Reddit-hosted videos
            if submission.is_video:
                video_url = submission.media['reddit_video']['fallback_url']
                success = download_media(video_url, submission.title, submission.id)
                if success:
                    # Record this submission ID to avoid future downloads
                    with open(downloaded_ids_file, "a", encoding="utf-8") as f:
                        f.write(submission.id + "\n")
                    downloaded_ids.add(submission.id)
                continue

            # Check for external video links (e.g., YouTube, etc.)
            if submission.url and any(ext in submission.url for ext in ['youtube.com', 'youtu.be', 'v.redd.it']):
                success = download_media(submission.url, submission.title, submission.id)
                if success:
                    with open(downloaded_ids_file, "a", encoding="utf-8") as f:
                        f.write(submission.id + "\n")
                    downloaded_ids.add(submission.id)
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")

if __name__ == '__main__':
    check_new_videos()
