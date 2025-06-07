"""
Initialize MongoDB with an empty events collection.
Run this script once to set up the MongoDB database and collection
with the correct schema validation.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def init_db():
    """Initialize MongoDB database with proper schema validation."""
    # Get MongoDB connection details from environment variables
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    collection_name = os.getenv("COLLECTION_NAME")
    
    if not mongo_uri or not db_name or not collection_name:
        print("Error: Missing MongoDB configuration in .env file")
        return
    
    print(f"Connecting to MongoDB at {mongo_uri}")
    print(f"Database: {db_name}")
    print(f"Collection: {collection_name}")
    
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Create collection if it doesn't exist
    if collection_name not in db.list_collection_names():
        print(f"Creating collection: {collection_name}")
        db.create_collection(collection_name)
    else:
        print(f"Collection {collection_name} already exists")
    
    # Schema validation for events collection
    # This is optional but helps ensure data consistency
    events_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["request_id", "author", "action", "timestamp"],
            "properties": {
                "request_id": {
                    "bsonType": "string",
                    "description": "Git commit hash or PR ID"
                },
                "author": {
                    "bsonType": "string",
                    "description": "GitHub username"
                },
                "action": {
                    "enum": ["PUSH", "PULL_REQUEST", "MERGE"],
                    "description": "GitHub action type"
                },
                "from_branch": {
                    "bsonType": "string",
                    "description": "Source branch name"
                },
                "to_branch": {
                    "bsonType": "string",
                    "description": "Target branch name"
                },
                "timestamp": {
                    "bsonType": "string",
                    "description": "ISO format datetime string"
                }
            }
        }
    }
    
    # Apply schema validation to the collection
    try:
        db.command({
            "collMod": collection_name,
            "validator": events_validator,
            "validationLevel": "moderate"
        })
        print("Schema validation applied to collection")
    except Exception as e:
        print(f"Warning: Could not apply schema validation: {e}")
    
    # Create index on timestamp for efficient sorting
    db[collection_name].create_index("timestamp")
    print("Created index on timestamp field")
    
    # Create index on action field for efficient filtering
    db[collection_name].create_index("action")
    print("Created index on action field")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
