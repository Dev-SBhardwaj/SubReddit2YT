"""
Utility functions for the Reddit to YouTube shorts automation project.
"""
import os
import re
import logging
from pathlib import Path
from typing import List, Optional
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def sanitize_filename(title: str) -> str:
    """
    Remove invalid characters from filenames and truncate long titles.
    
    Args:
        title: The input title string to sanitize
        
    Returns:
        A sanitized string safe for use as a filename
    """
    return re.sub(r'[\\/*?:"<>|]', '', title)[:50]

def read_file_content(file_path: Path) -> str:
    """
    Read the content of a file safely.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        String content of the file or empty string if file doesn't exist
    """
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return ""
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def write_file_content(file_path: Path, content: str) -> bool:
    """
    Write content to a file safely.
    
    Args:
        file_path: Path to the file to write
        content: String content to write to the file
        
    Returns:
        True if write was successful, False otherwise
    """
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return True
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False

def append_to_file(file_path: Path, content: str) -> bool:
    """
    Append content to a file safely.
    
    Args:
        file_path: Path to the file to append to
        content: String content to append to the file
        
    Returns:
        True if append was successful, False otherwise
    """
    try:
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(content)
        return True
    except Exception as e:
        logger.error(f"Error appending to file {file_path}: {e}")
        return False

def get_video_files(directory: Path = config.BASE_DIR) -> List[Path]:
    """
    Get all video files in a directory.
    
    Args:
        directory: Directory to search for video files
        
    Returns:
        List of Path objects for each video file found
    """
    video_files = []
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in config.VIDEO_EXTENSIONS:
            video_files.append(file)
    return video_files

def clear_file_content(file_path: Path) -> bool:
    """
    Clear the content of a file.
    
    Args:
        file_path: Path to the file to clear
        
    Returns:
        True if clearing was successful, False otherwise
    """
    return write_file_content(file_path, "")

def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    os.makedirs(directory, exist_ok=True)

def get_most_recent_video(directory: Path = config.BASE_DIR) -> Optional[Path]:
    """
    Get the most recently created video file in a directory.
    
    Args:
        directory: Directory to search for video files
        
    Returns:
        Path object for the most recent video file, or None if no videos found
    """
    video_files = get_video_files(directory)
    
    if not video_files:
        return None
        
    return max(video_files, key=lambda f: f.stat().st_ctime) 