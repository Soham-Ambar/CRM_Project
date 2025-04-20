import json
from pymongo import MongoClient
from urllib.parse import quote_plus
from prettytable import PrettyTable

# MongoDB connection details
username = "advaitkavishwar"
password = quote_plus("zerobalance@2025")  # URL-encode the password
MONGO_URI = f"mongodb+srv://{username}:{password}@db.s0gssbe.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "db"
COLLECTION_NAME = "crm_data"

def fetch_from_mongo():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Fetch all documents from the collection
    documents = collection.find()

    # Create a PrettyTable instance
    table = PrettyTable()
    table.field_names = ["_id", "Customer Name", "Email", "Phone", "Product Name", "Product Model", "Complaint"]

    # Add rows to the table
    for doc in documents:
        table.add_row([
            doc.get("_id", "N/A"),
            doc.get("customer_name", "N/A"),
            doc.get("email", "N/A"),
            doc.get("phone", "N/A"),
            doc.get("product_name", "N/A"),
            doc.get("product_model", "N/A"),
            doc.get("complaint", "N/A")
        ])

    # Print the table
    print(table)

if __name__ == "__main__":
    fetch_from_mongo()