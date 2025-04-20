import json
import time
import requests
import re  # Add this import to handle extracting JSON from the response
from pathlib import Path

# Configuration
API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"
INPUT_FILE = "../transcriptions/all_transcriptions.json"
OUTPUT_FILE = "../crm_data.json"
MODEL = "llama3-70b-8192"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def extract_crm_info(text):
    return [
        {"role": "system", "content": "You are a helpful assistant that extracts specific CRM fields from audio transcripts."},
        {
            "role": "user",
            "content": (
                "Extract the following information from the text below:\n"
                "- Customer Name\n- Email Address\n- Phone Number\n- Product Name\n"
                "- Product Model (if any)\n- Complaint About Product\n\n"
                "Return the data as a JSON object with keys: 'customer_name', 'email', 'phone', 'product_name', "
                "'product_model', and 'complaint'. If any information is missing, set its value to null.\n\n"
                "Text:\n\"\"\"\n" + text + "\n\"\"\""
            )
        }
    ]

def call_groq_api(transcript):
    payload = {
        "model": MODEL,
        "messages": extract_crm_info(transcript)
    }

    while True:
        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            if response.status_code == 429:
                print("🔁 Rate limit hit. Retrying in 10 seconds...")
                time.sleep(10)
                continue
            response.raise_for_status()
           # print(f"Raw API Response: {response.text}")  # Log the raw response
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

def main():
    # Load transcriptions
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = {}

    for audio_file, transcript in data.items():
        print(f"\n🔍 Processing: {audio_file}")
        print(f"📝 Text length: {len(transcript)}")

        response = call_groq_api(transcript)
        if response:
            try:
                # Extract JSON content from the response using regex
                match = re.search(r"```(.*?)```", response, re.DOTALL)
                if match:
                    json_content = match.group(1).strip()  # Extract JSON string
                    parsed = json.loads(json_content)  # Parse the JSON string
                    # Ensure all required keys are present, set missing ones to null
                    extracted_data = {
                        "customer_name": parsed.get("customer_name", None),
                        "email": parsed.get("email", None),
                        "phone": parsed.get("phone", None),
                        "product_name": parsed.get("product_name", None),
                        "product_model": parsed.get("product_model", None),
                        "complaint": parsed.get("complaint", None),
                    }
                    results[audio_file] = extracted_data
                    print(f"✅ Extracted CRM data for {audio_file}")
                else:
                    print(f"⚠️ No JSON content found in response for {audio_file}. Saving raw text.")
                    results[audio_file] = {"raw_response": response}
            except json.JSONDecodeError:
                print(f"⚠️ Failed to parse JSON content for {audio_file}. Saving raw text.")
                results[audio_file] = {"raw_response": response}
        else:
            print(f"⚠️ Skipping {audio_file} due to API failure.")

        # Delay between requests
        time.sleep(4)

    # Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
