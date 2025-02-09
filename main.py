import subprocess
import sys

def run_script(script_name):
    try:
        print(f"Executing {script_name}...")
        # Run the script using the default Python interpreter.
        # The check=True flag ensures that an exception is raised if the script fails.
        subprocess.run(["python", script_name], check=True)
        print(f"{script_name} executed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_name}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_script("GetVid.py")
    run_script("Title.py")
    run_script("YTUpload.py")
    run_script("ClearTitle.py")

