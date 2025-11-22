"""
Clears content from temporary files after processing is complete.
"""
import logging
from pathlib import Path
import os
import glob

import config
import utils

# Set up logger
logger = logging.getLogger(__name__)

def clear_files() -> bool:
    """
    Clear the content of temporary files used in the workflow and delete
    mp4 and jpg files leftover from Instagram uploads.
    
    Returns:
        True if all files were cleared successfully, False otherwise
    """
    # List of files to clear
    files_to_clear = [
        config.VID_TITLE_FILE,
        config.HASHTAG_FILE,
        config.FINAL_TITLE_FILE,
        config.DESC_FILE
    ]
    
    success = True
    # Clear content of text files
    for file_path in files_to_clear:
        try:
            if utils.clear_file_content(file_path):
                logger.info(f"Cleared file: {file_path}")
            else:
                success = False
                logger.warning(f"Failed to clear file: {file_path}")
        except Exception as e:
            success = False
            logger.error(f"Error clearing file {file_path}: {e}")
    
    # Delete mp4 and jpg files in the current directory
    try:
        # Find all mp4 and jpg files in the current directory
        mp4_files = glob.glob("*.mp4")
        jpg_files = glob.glob("*.jpg")
        
        # Delete mp4 files
        for file in mp4_files:
            try:
                os.remove(file)
                logger.info(f"Deleted file: {file}")
            except Exception as e:
                success = False
                logger.error(f"Error deleting file {file}: {e}")
        
        # Delete jpg files
        for file in jpg_files:
            try:
                os.remove(file)
                logger.info(f"Deleted file: {file}")
            except Exception as e:
                success = False
                logger.error(f"Error deleting file {file}: {e}")
                
    except Exception as e:
        success = False
        logger.error(f"Error during file cleanup: {e}")
    
    return success

if __name__ == "__main__":
    clear_files()
