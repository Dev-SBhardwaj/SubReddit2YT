import os

def clear_file(filename):
    """
    Opens the file in write mode to clear its content.
    If the file does not exist, it will be created.
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("")
        print(f"Cleared file: {filename}")
    except Exception as e:
        print(f"Error clearing file {filename}: {e}")

def main():
    # List of files to clear. Adjust the filenames as needed.
    files_to_clear = [
        "VidTitle.txt",
        "hashtag.txt",   # Adjust the case if needed (e.g., "Hashtag.txt")
        "FinalTitle.txt",
        "Desc.txt"
    ]
    
    for filename in files_to_clear:
        clear_file(filename)

if __name__ == "__main__":
    main()
