"""
Configuration settings for the Reddit to YouTube shorts automation project.
"""
import os
from pathlib import Path
from typing import Optional

def _get_env_setting(name: str, *, required: bool = False, default: Optional[str] = None) -> Optional[str]:
    """Fetch environment variables with optional required enforcement."""
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Environment variable '{name}' is required but not set.")
    return value

# Project directory structure
BASE_DIR = Path('.')
CHANNEL_VIDEOS_DIR = BASE_DIR / 'ChannelVideos'
CLIPS_DIR = CHANNEL_VIDEOS_DIR / 'Clips'

# Ensure directories exist
os.makedirs(CHANNEL_VIDEOS_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

# File paths
VID_TITLE_FILE = BASE_DIR / "VidTitle.txt"
FINAL_TITLE_FILE = BASE_DIR / "FinalTitle.txt"
DOWNLOADED_IDS_FILE = BASE_DIR / "downloaded_ids.txt"
SUBREDDIT_LIST_FILE = BASE_DIR / "AllReddit.txt"
DESC_FILE = BASE_DIR / "Desc.txt"
HASHTAG_FILE = BASE_DIR / "hashtag.txt"
YOUTUBE_VIDEO_IDS_FILE = BASE_DIR / "youtube_video_ids.txt"

# External tools configuration
FFMPEG_PATH = r"D:\Downloads\compressed\ffmpeg\bin"

# Reddit API credentials (set via environment variables)
REDDIT_CLIENT_ID = _get_env_setting("REDDIT_CLIENT_ID", required=True)
REDDIT_CLIENT_SECRET = _get_env_setting("REDDIT_CLIENT_SECRET", required=True)
REDDIT_USER_AGENT = _get_env_setting(
    "REDDIT_USER_AGENT",
    default="VideoDownloader/1.0 (by /u/"your reddit username")",
)

# YouTube API configuration (set via environment variables)
YOUTUBE_CLIENT_ID = _get_env_setting("YOUTUBE_CLIENT_ID", required=True)
YOUTUBE_CLIENT_SECRET = _get_env_setting("YOUTUBE_CLIENT_SECRET", required=True)
YOUTUBE_PROJECT_ID = _get_env_setting("YOUTUBE_PROJECT_ID", required=True)
YOUTUBE_API_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Instagram credentials (set via environment variables)
INSTAGRAM_USERNAME = _get_env_setting("INSTAGRAM_USERNAME", required=True)
INSTAGRAM_PASSWORD = _get_env_setting("INSTAGRAM_PASSWORD", required=True)
INSTAGRAM_SESSION_FILE = BASE_DIR / "instagram_session.json"

# Video processing settings
MAX_VIDEO_DURATION = 120  # seconds
VIDEO_HEIGHT = 1920
VIDEO_WIDTH = 1080
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov')