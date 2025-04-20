import json
from pymongo import MongoClient
from urllib.parse import quote_plus
import time

# MongoDB connection details
username = "advaitkavishwar"
password = quote_plus("zerobalance@2025")  # URL-encode the password
MONGO_URI = f"mongodb+srv://{username}:{password}@db.s0gssbe.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "db"
COLLECTION_NAME = "crm_data"

# Filepath to the JSON file
JSON_FILE_PATH = "../crm_data.json"

def upload_to_mongo():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Read the JSON file
    with open(JSON_FILE_PATH, "r") as file:
        data = json.load(file)

    # Convert the data to a list of documents
    documents = []
    for key, value in data.items():
        # Append a timestamp to the _id to make it unique
        unique_id = f"{key}_{int(time.time())}"
        documents.append({"_id": unique_id, **value})

    # Insert the documents into the collection
    try:
        collection.insert_many(documents, ordered=False)
        print("✅ Data uploaded successfully!")
    except Exception as e:
        print(f"❌ Error uploading data: {e}")

if __name__ == "__main__":
    upload_to_mongo()