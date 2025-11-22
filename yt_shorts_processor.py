"""
Processes videos to make them suitable for YouTube Shorts format.
"""
import os
import logging
from pathlib import Path
from moviepy.editor import VideoFileClip
from PIL import Image

import config
import utils

# Set up logger
logger = logging.getLogger(__name__)

# Fix for newer Pillow versions where ANTIALIAS is deprecated
if not hasattr(Image, 'ANTIALIAS'):
    # For Pillow >= 9.0.0
    Image.ANTIALIAS = Image.LANCZOS

class VideoProcessor:
    """Class for processing videos for YouTube Shorts format."""
    
    def __init__(self, input_dir: Path = config.BASE_DIR, 
                 output_dir: Path = config.CLIPS_DIR,
                 target_height: int = config.VIDEO_HEIGHT,
                 target_width: int = config.VIDEO_WIDTH,
                 max_duration: int = config.MAX_VIDEO_DURATION):
        """
        Initialize the VideoProcessor.
        
        Args:
            input_dir: Directory containing input videos
            output_dir: Directory for processed videos
            target_height: Target height for the processed video
            target_width: Target width for the processed video
            max_duration: Maximum video duration in seconds
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_height = target_height
        self.target_width = target_width
        self.max_duration = max_duration
        
        # Create the output directory if it doesn't exist
        utils.ensure_directory_exists(output_dir)
        
    def process_video(self, file_path: Path) -> bool:
        """
        Process a single video file.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing {file_path.name} ...")
            
            # Load the video clip
            clip = VideoFileClip(str(file_path))
            
            # Trim the video to max_duration seconds if it's longer
            if clip.duration > self.max_duration:
                clip = clip.subclip(0, self.max_duration)
            
            # Save a copy of the trimmed clip to the output folder
            dest_file_path = self.output_dir / file_path.name
            clip.write_videofile(str(dest_file_path), codec="libx264", audio_codec="aac")
            logger.info(f"Saved copy to {dest_file_path}")
            
            # Resize the video to match target height
            clip = clip.resize(height=self.target_height)
            
            # Crop the clip to get a centered region with target width
            clip = clip.crop(x_center=clip.w/2, width=self.target_width)
            
            # Define a temporary output file path in the same directory
            temp_output_path = file_path.parent / f"temp_{file_path.name}"
            
            # Write the processed video to the temporary file
            clip.write_videofile(str(temp_output_path), codec="libx264", audio_codec="aac")
            
            # Close the clip to release resources
            clip.close()
            
            # Replace the original file with the processed file
            file_path.unlink()
            temp_output_path.rename(file_path)
            
            logger.info(f"Converted and replaced {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return False
            
    def process_all_videos(self) -> int:
        """
        Process only the most recently downloaded video file.
        
        Returns:
            Number of successfully processed videos (0 or 1)
        """
        most_recent_video = utils.get_most_recent_video(self.input_dir)
        
        if not most_recent_video:
            logger.info("No video files found to process")
            return 0
            
        logger.info(f"Processing most recently downloaded video: {most_recent_video.name}")
        
        if self.process_video(most_recent_video):
            return 1
        else:
            return 0

def process_videos():
    """
    Process videos in the input directory for YouTube Shorts format.
    
    Returns:
        True if at least one video was processed successfully, False otherwise
    """
    try:
        processor = VideoProcessor()
        processed_count = processor.process_all_videos()
        return processed_count > 0
    except Exception as e:
        logger.error(f"Error in video processing: {str(e)}")
        return False

if __name__ == "__main__":
    process_videos()
