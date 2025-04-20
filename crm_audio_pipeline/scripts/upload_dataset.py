import os
import cloudinary
import cloudinary.uploader

# Step 1: Configure Cloudinary credentials
cloudinary.config(
    cloud_name='da6ritn8r',
    api_key='954973651148753',
    api_secret='sgD5Vq4ZnDB81QCoaUTX0C8HQqc'
)

# Step 2: Set path to 'audio_dataset' folder
base_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/ directory
dataset_dir = os.path.join(base_dir, '..', 'audio_dataset')  # navigate to ../audio_dataset

# Step 3: Upload all audio files
def upload_audio_dataset():
    for filename in os.listdir(dataset_dir):
        if filename.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a')):
            file_path = os.path.join(dataset_dir, filename)
            print(f"Uploading: {filename}")

            response = cloudinary.uploader.upload(
                file_path,
                resource_type="video",  # Cloudinary treats audio/video together
                folder="crm_audio_dataset"  # Optional: Cloudinary folder name
            )

            print("✔ Uploaded:", response['secure_url'])

if __name__ == "__main__":
    upload_audio_dataset()
