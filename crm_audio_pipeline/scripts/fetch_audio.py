import sys
import requests
from pathlib import Path
import cloudinary
import cloudinary.api
import subprocess

# Cloudinary configuration
cloudinary.config(
    cloud_name="da6ritn8r",
    api_key="954973651148753",
    api_secret="sgD5Vq4ZnDB81QCoaUTX0C8HQqc"
)

CLOUDINARY_FOLDER = "crm_audio_dataset"
AUDIO_FILES_DIR = "../audio_files"  # Directory to save fetched files
FETCHED_FILES_RECORD = "fetched_files.txt"  # File to track fetched files
PROCESSED_FILES_RECORD = "processed_files.txt"  # File to track processed files

def load_fetched_files():
    """Load the list of already fetched files from the record."""
    if not Path(FETCHED_FILES_RECORD).exists():
        return set()
    with open(FETCHED_FILES_RECORD, "r") as f:
        return set(line.strip() for line in f)

def load_processed_files():
    """Load the list of already processed files from the record."""
    if not Path(PROCESSED_FILES_RECORD).exists():
        return set()
    with open(PROCESSED_FILES_RECORD, "r") as f:
        return set(line.strip() for line in f)

def save_fetched_file(public_id):
    """Save a fetched file's public_id to the record."""
    with open(FETCHED_FILES_RECORD, "a") as f:
        f.write(f"{public_id}\n")

def save_processed_file(public_id):
    """Save a processed file's public_id to the record."""
    with open(PROCESSED_FILES_RECORD, "a") as f:
        f.write(f"{public_id}\n")

def fetch_audio(public_id, extension="wav"):  # Default extension is .wav
    fetched_files = load_fetched_files()
    if public_id in fetched_files:
        print(f"⚠️ File '{public_id}' already fetched. Skipping fetch step.")
        # Trigger the pipeline for already fetched files
        trigger_pipeline(public_id)
        return

    # Construct the URL for the file
    url = f"https://res.cloudinary.com/da6ritn8r/video/upload/{CLOUDINARY_FOLDER}/{public_id}.{extension}"
    print(f"Fetching from URL: {url}")  # Debugging log

    # Fetch the file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Ensure the audio_files directory exists
        Path(AUDIO_FILES_DIR).mkdir(parents=True, exist_ok=True)

        # Save the file to the audio_files directory
        output_path = Path(AUDIO_FILES_DIR) / f"{public_id}.{extension}"
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Audio file saved: {output_path}")

        # Mark the file as fetched
        save_fetched_file(public_id)

        # Trigger the next steps in the pipeline
        trigger_pipeline(public_id)
    else:
        print(f"❌ Failed to fetch audio file: {response.status_code}")

def fetch_all_files():
    """Fetch all files from the Cloudinary folder."""
    fetched_files = load_fetched_files()
    print("🔍 Fetching file list from Cloudinary...")
    try:
        # Get the list of files in the Cloudinary folder
        resources = cloudinary.api.resources(
            type="upload",
            prefix=CLOUDINARY_FOLDER,
            resource_type="video"
        )["resources"]

        # Iterate through the files and fetch them if not already fetched
        for resource in resources:
            public_id = resource["public_id"].split("/")[-1]  # Extract the file name
            if public_id not in fetched_files:
                print(f"⬇️ Fetching file: {public_id}")
                fetch_audio(public_id, extension="wav")
            else:
                print(f"⚠️ File '{public_id}' already fetched. Checking pipeline status...")
                trigger_pipeline(public_id)  # Trigger pipeline for already fetched files
    except Exception as e:
        print(f"❌ Failed to fetch file list from Cloudinary: {e}")

def trigger_pipeline(public_id):
    """Trigger the transcription, extraction, and upload steps for a specific file."""
    processed_files = load_processed_files()
    if public_id in processed_files:
        print(f"⚠️ File '{public_id}' already processed. Skipping pipeline.")
        return

    try:
        # Get the Python interpreter from the current environment
        python_executable = sys.executable

        # Step 1: Transcribe audio files
        print("\n🔄 Starting transcription...")
        subprocess.run([python_executable, "transcribe_audio.py"], check=True)

        # Step 2: Extract information using groq.py
        print("\n🔄 Extracting information...")
        subprocess.run([python_executable, "groq.py"], check=True)

        # Step 3: Upload data to MongoDB
        print("\n🔄 Uploading data to MongoDB...")
        subprocess.run([python_executable, "upload_to_mongo.py"], check=True)

        # Mark the file as processed
        save_processed_file(public_id)

        print("\n✅ CRM pipeline completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during pipeline execution: {e}")

if __name__ == "__main__":
    # Ensure the audio_files directory exists
    Path(AUDIO_FILES_DIR).mkdir(parents=True, exist_ok=True)

    # Fetch all files from Cloudinary
    fetch_all_files()
