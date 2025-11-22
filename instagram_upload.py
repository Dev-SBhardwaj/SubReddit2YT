from instagrapi import Client
import glob
from pathlib import Path

import config

def read_file_content(filename):
    """Read and return the content of a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return ""

def _initialize_client() -> Client:
    """Initialize Instagram client loading cached session if available."""
    cl = Client()
    session_path = config.INSTAGRAM_SESSION_FILE
    if Path(session_path).exists():
        try:
            cl.load_settings(str(session_path))
            print("Loaded Instagram session settings.")
        except Exception as exc:
            print(f"Warning: Failed to load Instagram session settings: {exc}")
    return cl


def upload_video_to_instagram():
    """Upload video to Instagram with caption and hashtags.
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    # Instagram credentials sourced from environment variables
    username = config.INSTAGRAM_USERNAME
    password = config.INSTAGRAM_PASSWORD

    # Initialize client
    cl = _initialize_client()
    
    try:
        # Direct login
        print("Logging in to Instagram...")
        cl.login(username, password)
        print("Login successful")

        # Get video files
        video_files = glob.glob("*.mp4")
        if not video_files:
            print("No video files found")
            return False

        video_file = video_files[0]
        caption = read_file_content("FinalTitle.txt")
        hashtags = read_file_content("hashtag.txt")
        
        # Format hashtags with line breaks for better compatibility
        if " " in hashtags:
            hashtag_list = hashtags.split()
            hashtags = " ".join(hashtag_list)

        full_caption = f"{caption}\n\n{hashtags}"
        print(f"Uploading video: {video_file}")

        try:
            # Upload video with full caption
            print("Attempting upload...")
            media = cl.clip_upload(video_file, caption=full_caption)
            if media:
                print("Successfully uploaded video")
                return True
            else:
                print("Upload failed: No media response")
                return False
        
        except Exception as e:
            print(f"Upload failed: {e}")
            return False

    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    
    finally:
        cl.logout()
        print("Logged out of Instagram")

if __name__ == "__main__":
    upload_video_to_instagram()