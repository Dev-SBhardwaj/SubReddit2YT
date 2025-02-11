import os
from moviepy.editor import VideoFileClip

# Define the directory containing the video files.
input_dir = r"ENTER_YOUR_DOWNLOADED_VIDEO_PATH"

# Define allowed video file extensions.
allowed_ext = [".mp4", ".mov", ".avi", ".mkv"]

# Loop through all files in the input directory.
for filename in os.listdir(input_dir):
    # Build full path for the file.
    file_path = os.path.join(input_dir, filename)
    
    # Process only files with allowed extensions.
    if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in allowed_ext:
        print(f"Processing {filename} ...")
        
        try:
            # Load the video clip.
            clip = VideoFileClip(file_path)
            
            # Trim the video to 120 seconds if longer.
            if clip.duration > 120:
                clip = clip.subclip(0, 120)
            
            # Resize the video so that its height is 1920 pixels.
            clip = clip.resize(height=1920)
            
            # Crop the clip to get a centered region with a width of 1080 pixels.
            clip = clip.crop(x_center=clip.w/2, width=1080)
            
            # Define a temporary output file path in the same directory.
            temp_output_path = os.path.join(input_dir, "temp_" + filename)
            
            # Write the converted video to the temporary file.
            clip.write_videofile(temp_output_path, codec="libx264", audio_codec="aac")
            
            # Close the clip to release resources.
            clip.close()
            
            # Delete the original file.
            os.remove(file_path)
            
            # Rename the temporary file to the original file name.
            os.rename(temp_output_path, file_path)
            
            print(f"Converted and replaced {filename}.")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
