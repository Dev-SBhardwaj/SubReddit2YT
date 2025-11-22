"""
Uses Gemini AI to enhance video titles, generate descriptions, and hashtags.
"""
import google.generativeai as genai
import os
import logging
from typing import Tuple, Optional

import config
import utils

# Set up logger
logger = logging.getLogger(__name__)

class ContentGenerator:
    """Class for generating enhanced content using Google's Gemini AI."""
    
    def __init__(self, api_key: str = os.getenv("GEMINI_API_KEY")):
        """
        Initialize the ContentGenerator with Gemini API.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY environment variable)
        """
        if not api_key:
            logger.error("Gemini API key not provided. Set the GEMINI_API_KEY environment variable.")
            raise ValueError("Gemini API key not provided")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        self.model_name = "models/gemini-2.0-flash-thinking-exp"
        
    def generate_enhanced_content(self, original_title: str) -> Tuple[str, str, str]:
        """
        Generate enhanced title, description, and hashtags based on original title.
        
        Args:
            original_title: The original video title
            
        Returns:
            Tuple containing enhanced title, description, and hashtags
        """
        prompt = (
            f"Make this video title more interesting: '{original_title}'.\n"
            "Also, provide a one-line description and at least 20 suitable hashtags. "
            "Return the response in the format: \nTitle: [New Title]\nDescription: [One-line Description]\nHashtags: [Comma-separated hashtags]"
        )
        
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse AI response
            title, description, hashtags = self._parse_response(result)
            
            # Ensure #shorts is included in hashtags
            if hashtags and "#shorts" not in hashtags:
                hashtags = f"{hashtags}, #shorts, #viral"
            else:
                hashtags = f"{hashtags}, #shorts, #viral"
                
            return title, description, hashtags
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return original_title, "", "#shorts"
    
    def _parse_response(self, response: str) -> Tuple[str, str, str]:
        """
        Parse the AI response into title, description, and hashtags.
        
        Args:
            response: Raw response from Gemini AI
            
        Returns:
            Tuple containing title, description, and hashtags
        """
        lines = response.split("\n")
        title, description, hashtags = "", "", ""
        
        for line in lines:
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
            elif line.startswith("Hashtags:"):
                hashtags = line.replace("Hashtags:", "").strip()
                
        return title, description, hashtags

def enhance_video_title() -> bool:
    """
    Read the most recently downloaded video title, enhance it with AI, and save the results.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the title from VidTitle.txt
        original_title = utils.read_file_content(config.VID_TITLE_FILE)
        
        if not original_title:
            logger.warning("[WARNING] VidTitle.txt is empty! Please provide a valid title.")
            return False
            
        logger.info(f"Enhancing title: {original_title}")
            
        # Generate enhanced content
        try:
            content_generator = ContentGenerator()
            title, description, hashtags = content_generator.generate_enhanced_content(original_title)
        except ValueError as e:
            logger.error(f"Failed to initialize ContentGenerator: {str(e)}")
            return False
            
        # Save outputs to respective files
        utils.write_file_content(config.FINAL_TITLE_FILE, title)
        utils.write_file_content(config.DESC_FILE, description)
        utils.write_file_content(config.HASHTAG_FILE, hashtags)
        
        logger.info("[SUCCESS] AI-generated content saved successfully!")
        logger.info(f"[INFO] Final Title: {title}")
        logger.info(f"[INFO] Description: {description}")
        logger.info(f"[INFO] Hashtags: {hashtags}")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Error enhancing video title: {str(e)}")
        return False

if __name__ == '__main__':
    enhance_video_title()