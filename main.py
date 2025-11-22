"""
Main script for Reddit to YouTube Shorts automation workflow.
"""
import logging
import sys
from pathlib import Path
import time

import config
import utils
from GetVid import check_new_videos
from Title import enhance_video_title
from yt_shorts_processor import process_videos
from YTUpload import upload_and_delete, cleanup_files
from instagram_upload import upload_video_to_instagram
from ClearTitle import clear_files

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_workflow() -> bool:
    """
    Run the complete Reddit to YouTube workflow:
    1. Find and download ONE new video from Reddit
    2. Generate an enhanced title using AI
    3. Process the video for YouTube Shorts format
    4. Upload the video to Instagram
    5. Upload the video to YouTube
    6. Clean up temporary files
    
    The workflow processes only one video at a time and stops if any step fails.
    
    Returns:
        True if the workflow completed successfully, False otherwise
    """
    success = True
    
    try:
        steps = [
            ("Downloading video from Reddit", check_new_videos),
            ("Enhancing video title", enhance_video_title),
            ("Processing video for YouTube Shorts", process_videos),
            ("Uploading video to Instagram", upload_video_to_instagram),
            ("Uploading video to YouTube", upload_and_delete),
        ]
        
        for i, (step_name, step_function) in enumerate(steps):
            step_number = i + 1
            logger.info(f"Step {step_number}/{len(steps)}: {step_name}")
            
            try:
                result = step_function()
                if result:
                    logger.info(f"[SUCCESS] Step {step_number} completed successfully!")
                else:
                    logger.error(f"[FAILED] Step {step_number} failed. Stopping workflow.")
                    success = False
                    break
            except Exception as e:
                logger.error(f"[ERROR] Step {step_number} failed with error: {str(e)}")
                success = False
                break
                
            # Short pause between steps for better logging readability
            time.sleep(1)
        
        if success:
            logger.info("[SUCCESS] Complete workflow executed successfully!")
    
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error in workflow: {str(e)}")
        success = False
    
    finally:
        # Always ensure cleanup is performed, regardless of workflow outcome
        logger.info("Running final cleanup to ensure no files are left over...")
        try:
            # First try using our dedicated cleanup function
            cleanup_result = cleanup_files()
            if not cleanup_result:
                logger.warning("First cleanup attempt was not fully successful, trying backup cleanup...")
                # If that doesn't fully succeed, try the backup method
                clear_files()
            
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during final cleanup: {str(e)}")
    
    return success

if __name__ == "__main__":
    # Ensure all necessary directories exist
    for directory in [config.BASE_DIR, config.CHANNEL_VIDEOS_DIR, config.CLIPS_DIR]:
        utils.ensure_directory_exists(directory)
    
    # Run the workflow and return appropriate exit code
    success = run_workflow()
    sys.exit(0 if success else 1)
