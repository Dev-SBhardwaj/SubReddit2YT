import os
import googleapiclient.discovery
import google_auth_oauthlib.flow

# YouTube OAuth credentials
CLIENT_ID = "ENTER_YOUR_CLIENT_ID"
CLIENT_SECRET = "ENTER_YOUR_CLIENT_SECRET"

# YouTube API setup  
API_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Video directory details
VIDEO_DIR = r"ENTER_YOUR_VIDEO_PATH_HERE"  # Directory containing downloaded videos

# Allowed video file extensions
video_extensions = ('.mp4', '.mkv', '.avi', '.mov')

# List all video files in the directory (ignoring case)
video_files = [
    f for f in os.listdir(VIDEO_DIR)
    if f.lower().endswith(video_extensions)
]

if not video_files:
    print("No video files found in the directory. Exiting.")
    exit(0)

# For this example, choose the first video file found.
VIDEO_FILE = os.path.join(VIDEO_DIR, video_files[0])
print(f"Found video file: {VIDEO_FILE}")

# Read title from FinalTitle.txt
with open("FinalTitle.txt", "r", encoding="utf-8") as title_file:
    title = title_file.read().strip()

# Read description from Desc.txt
with open("Desc.txt", "r", encoding="utf-8") as desc_file:
    description = desc_file.read().strip()

# Read hashtags from hashtag.txt and append them to the description
with open("hashtag.txt", "r", encoding="utf-8") as hashtag_file:
    hashtags = hashtag_file.read().strip()

# Optionally, add a newline or separator between the description and hashtags
description = f"{description}\n\n{hashtags}"

# Auth flow to get credentials
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
    client_config={
        "web": {
            "client_id": CLIENT_ID,
            "project_id": "ENTER_YOUR_PROJECT_NAME",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": CLIENT_SECRET
        }
    },
    scopes=SCOPES
)
credentials = flow.run_local_server()

# Build YouTube API client
youtube = googleapiclient.discovery.build(API_NAME, API_VERSION, credentials=credentials)

def upload_and_delete(youtube, video_file, title, description):
    # Upload video to YouTube
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "videoCategory": "28",  # Adjust to your desired category
            },
            "status": {
                "privacyStatus": "public"  # Video will be public after upload
            }
        },
        media_body=video_file
    )

    response = request.execute()

    youtube_video_id = response['id']
    print("Video uploaded with ID:", youtube_video_id)

    # Delete video file after successful upload
    os.remove(video_file)
    print("Video file deleted")

    # Save the uploaded YouTube video ID to file
    with open('youtube_video_ids.txt', 'a', encoding="utf-8") as id_file:
        id_file.write(youtube_video_id + '\n')
    print("Video ID saved to file")

# Call the function to upload and delete the selected video
upload_and_delete(youtube, VIDEO_FILE, title, description)
