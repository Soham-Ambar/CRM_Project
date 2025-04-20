import os
import whisper
import json
import torch

# Step 1: Check if GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Step 2: Initialize Whisper model
model = whisper.load_model("small", device=device)  # Change to "medium" or "large" if needed

# Step 3: Define folders
input_dir = os.path.join(os.path.dirname(__file__), '..', 'audio_files')
output_dir = os.path.join(os.path.dirname(__file__), '..', 'transcriptions')
os.makedirs(output_dir, exist_ok=True)

# Step 4: Prepare dictionary to store all results
all_transcriptions = {}

# Step 5: Loop through each audio file
for filename in os.listdir(input_dir):
    if not filename.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a')):
        continue

    input_path = os.path.join(input_dir, filename)

    print(f"Transcribing: {filename}")
    result = model.transcribe(input_path)
    all_transcriptions[filename] = result["text"]

# Step 6: Save all transcriptions to a JSON file
output_path = os.path.join(output_dir, "all_transcriptions.json")
with open(output_path, "w") as f:
    json.dump(all_transcriptions, f, indent=4)

print(f"✅ All transcriptions saved to: {output_path}")

