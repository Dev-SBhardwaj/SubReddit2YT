# SubReddit2YT

SubReddit2YT is an automation tool that downloads videos from a specified subreddit, enhances the video title using AI (Gemini AI by default), generates a compelling description and hashtags, and finally uploads the video to a specified YouTube channel.

## Features

- **Automated Video Download:** Downloads videos from a user-specified subreddit.
- **AI-Powered Title & Description Generation:** Uses Gemini AI (or other AI alternatives) to generate an engaging title, description, and hashtags based on the video file.
- **YouTube Upload:** Automatically uploads the processed video to a designated YouTube channel.
- **Easy Configuration:** Customize your API keys, client IDs, and paths directly within the configuration files.

## Setup and Configuration

### 1. Reddit Configuration

Edit the `GetVid.py` file to configure your Reddit credentials and settings:

- **Client ID and Secret:**  
  Add your Reddit client ID and secret.

- **User Agent:**  
  Update the `user_agent` with your Reddit username:  
  ```python
  user_agent = 'VideoDownloader/1.0 (by /u/Yourusername)'

    Subreddit Name:
    Specify the subreddit you wish to extract videos from:

subreddit_name = 'Name'

Download Directory:
Define the path where downloaded videos should be saved:

    download_dir = r'path/directory'

### 2. Gemini AI (or Alternative AI) Configuration

The Title.py file uses Gemini AI to generate a title, description, and hashtags. If you prefer to use another AI service, make sure you add and configure the appropriate API keys.

    Gemini AI API Key:
    Ensure that you have set your Gemini API key in your system’s environment variables as follows:

    # Set Google Gemini API key
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Ensure to set the environment variable

    If you switch to another AI, update the code accordingly and ensure that the API key is properly configured.

### 3. YouTube Configuration

Before uploading videos to YouTube, update your YouTube API credentials in the relevant configuration section (likely within a dedicated configuration file or within the upload script):

    CLIENT_ID and CLIENT_SECRET:
    Add your YouTube CLIENT_ID and CLIENT_SECRET.

    Video Directory:
    Specify the path of the directory containing videos to be uploaded.

    Project ID:
    Update the "project_id": "" field with the project ID obtained during your YouTube API authentication setup.

### Usage

    Clone the Repository:

git clone https://github.com/yourusername/SubReddit2YT.git
cd SubReddit2YT

Configure the Settings:

    Update GetVid.py with your Reddit credentials, subreddit name, and download directory.
    Update Title.py with your Gemini AI (or alternative AI) configuration.
    Set your YouTube credentials and project details in the YouTube configuration section.

Set Environment Variables (for Gemini AI): Ensure your Gemini API key is set in your system environment:

export GEMINI_API_KEY='your_gemini_api_key'

(For Windows, use set GEMINI_API_KEY=your_gemini_api_key)

### Prerequisites

Before running the application, ensure you have installed the necessary libraries. In particular, install the yt_dlp library:

pip install yt_dlp

### Execution

After configuring your API keys, client IDs, and secrets, you can run the main application using your favorite Python IDE or via the command line:

python main.py

This will execute the entire automation process, including video downloading, title and description generation, and uploading to YouTube.

### Contributing

Feel free to fork this repository, make modifications, add features, or update the code as needed. Contributions are always welcome! Please follow the standard GitHub flow for your pull requests.
License

This project is open source and available under the MIT License.

Happy coding and enjoy automating your video uploads!


---

Feel free to adjust any section to better match your project’s specifics or any future changes. Enjoy using **SubReddit2YT**!

