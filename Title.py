import google.generativeai as genai
import os

# Set Google Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Ensure to set the environment variable

def enhance_video_title():
    """
    Reads a video title from VidTitle.txt, sends it to Gemini AI to generate an engaging title,
    a one-line description, and suitable hashtags (with #shorts appended), then saves them in separate files.
    """
    try:
        # Read the title from VidTitle.txt
        with open("VidTitle.txt", "r", encoding="utf-8") as file:
            original_title = file.read().strip()

        if not original_title:
            print("⚠️ VidTitle.txt is empty! Please provide a valid title.")
            return

        # Prompt for AI
        prompt = (
            f"Make this video title more interesting: '{original_title}'.\n"
            "Also, provide a one-line description and suitable hashtags. "
            "Return the response in the format: \nTitle: [New Title]\nDescription: [One-line Description]\nHashtags: [Comma-separated hashtags]"
        )

        # Generate response from Gemini AI
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        result = response.text.strip()

        # Parse AI response
        lines = result.split("\n")
        title, description, hashtags = "", "", ""
        
        for line in lines:
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
            elif line.startswith("Hashtags:"):
                hashtags = line.replace("Hashtags:", "").strip()

        # Append "#shorts" to the hashtags if it's not already included.
        if "#shorts" not in hashtags:
            if hashtags:
                hashtags = f"{hashtags}, #shorts"
            else:
                hashtags = "#shorts"

        # Save outputs to respective files
        with open("FinalTitle.txt", "w", encoding="utf-8") as file:
            file.write(title)

        with open("Desc.txt", "w", encoding="utf-8") as file:
            file.write(description)

        with open("Hashtag.txt", "w", encoding="utf-8") as file:
            file.write(hashtags)

        print("\n✅ AI-generated content saved successfully!")
        print(f"\n🔹 Final Title: {title}\n🔹 Description: {description}\n🔹 Hashtags: {hashtags}")
    
    except Exception as e:
        print("❌ Error:", e)

# Run the function
enhance_video_title()
