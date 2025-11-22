"""
Uploads processed videos to YouTube as Shorts.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import googleapiclient.discovery
import google_auth_oauthlib.flow

import config
import utils

# Set up logger
logger = logging.getLogger(__name__)

class YouTubeUploader:
    """Class for uploading videos to YouTube with secure credential loading."""
    
    def __init__(self,
                 client_id: str | None = None,
                 client_secret: str | None = None,
                 api_name: str = config.YOUTUBE_API_NAME,
                 api_version: str = config.YOUTUBE_API_VERSION,
                 scopes: list = config.YOUTUBE_SCOPES,
                 project_id: str | None = None):
        """
        Initialize the YouTube uploader.
        
        Args:
            client_id: YouTube OAuth client ID
            client_secret: YouTube OAuth client secret
            api_name: YouTube API name
            api_version: YouTube API version
            scopes: YouTube API scopes
            project_id: Google Cloud project ID
        """
        self.client_id = client_id or config.YOUTUBE_CLIENT_ID
        self.client_secret = client_secret or config.YOUTUBE_CLIENT_SECRET
        self.api_name = api_name
        self.api_version = api_version
        self.scopes = scopes
        self.project_id = project_id or config.YOUTUBE_PROJECT_ID
        self.youtube = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API.
        
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            # Auth flow to get credentials
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.client_id,
                        "project_id": self.project_id,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": self.client_secret
                    }
                },
                scopes=self.scopes
            )
            credentials = flow.run_local_server()
            
            # Build YouTube API client
            self.youtube = googleapiclient.discovery.build(
                self.api_name, 
                self.api_version, 
                credentials=credentials
            )
            logger.info("Successfully authenticated with YouTube API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def upload_video(self, video_file: Path, title: str, description: str, tags: list) -> Optional[str]:
        """
        Upload a video to YouTube.
        
        Args:
            video_file: Path to the video file
            title: Video title
            description: Video description
            tags: List of tags for the video
            
        Returns:
            YouTube video ID if successful, None otherwise
        """
        if not self.youtube:
            logger.error("YouTube API client not initialized. Call authenticate() first.")
            return None
            
        if not video_file.exists():
            logger.error(f"Video file not found: {video_file}")
            return None
            
        try:
            logger.info(f"Uploading video: {title}")
            
            # Upload video to YouTube with the 'selfDeclaredMadeForKids' flag set to False
            request = self.youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "categoryId": "24",  # Entertainment category
                        "defaultLanguage": "en",
                        "localized": {
                            "title": title,
                            "description": description
                        }
                    },
                    "status": {
                        "privacyStatus": "public",  # Video will be public after upload
                        "selfDeclaredMadeForKids": False,  # This sets the video as NOT made for kids
                        "containsSyntheticMedia": False  # This property discloses if a video contains realistic altered content
                    }
                },
                media_body=str(video_file)
            )
            
            response = request.execute()
            youtube_video_id = response['id']
            
            logger.info(f"Video uploaded successfully with ID: {youtube_video_id}")
            return youtube_video_id
            
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return None

def upload_and_delete() -> bool:
    """
    Upload the most recently processed video to YouTube and delete it after successful upload.
    
    Returns:
        True if upload was successful, False otherwise
    """
    upload_success = False
    video_file = None
    cleanup_success = True
    
    # Read content from files
    title = utils.read_file_content(config.FINAL_TITLE_FILE)
    description = utils.read_file_content(config.DESC_FILE)
    hashtags = utils.read_file_content(config.HASHTAG_FILE)
    
    # Validate content
    if not title:
        logger.error("No title found in FinalTitle.txt")
        # Even if there's no title, clean up files before returning
        cleanup_files()
        return False
        
    # Format description with hashtags
    full_description = description
    if hashtags:
        full_description = f"{description}\n\n{hashtags}"
        
    # Get hashtags as a list (for tags parameter)
    tags_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
    
    try:
        # Get the most recent video file
        video_file = utils.get_most_recent_video()
        
        if not video_file:
            logger.info("No video files found to upload.")
            # Clean up any potential files that might still be there
            cleanup_files()
            return False
            
        logger.info(f"Found most recent video file: {video_file}")
        
        # Initialize uploader and authenticate
        uploader = YouTubeUploader()
        if not uploader.authenticate():
            # Clean up files even if authentication fails
            cleanup_files()
            return False
            
        # Upload video
        youtube_video_id = uploader.upload_video(video_file, title, full_description, tags_list)
        
        upload_success = youtube_video_id is not None
        
        if upload_success:
            # Save the uploaded YouTube video ID to file
            utils.append_to_file(config.YOUTUBE_VIDEO_IDS_FILE, f"{youtube_video_id}\n")
            logger.info("Video ID saved to file")
    
    except Exception as e:
        logger.error(f"Error in upload process: {str(e)}")
        upload_success = False
    
    # Always clean up files regardless of what happened in the try block
    if not cleanup_files():
        cleanup_success = False
    
    # Only return True if both upload and cleanup succeeded
    return upload_success and cleanup_success

def cleanup_files() -> bool:
    """
    Clean up MP4 and JPG files from the current directory.
    This function will be called regardless of upload success or failure.
    
    Returns:
        True if all files were cleaned up successfully, False otherwise
    """
    cleanup_success = True
    try:
        # Find all mp4 and jpg files in the current directory
        import glob
        mp4_files = glob.glob("*.mp4")
        jpg_files = glob.glob("*.jpg")
        
        logger.info(f"Found {len(mp4_files)} MP4 files and {len(jpg_files)} JPG files to clean up")
        
        # Close any potential file handles before deletion
        import gc
        gc.collect()
        
        # Delete mp4 files
        for file in mp4_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    logger.info(f"Deleted MP4 file: {file}")
            except Exception as e:
                cleanup_success = False
                logger.error(f"Error deleting file {file}: {e}")
        
        # Delete jpg files
        for file in jpg_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    logger.info(f"Deleted JPG file: {file}")
            except Exception as e:
                cleanup_success = False
                logger.error(f"Error deleting file {file}: {e}")
                
    except Exception as e:
        cleanup_success = False
        logger.error(f"Error during file cleanup: {e}")
    
    return cleanup_success

if __name__ == "__main__":
    upload_and_delete()
