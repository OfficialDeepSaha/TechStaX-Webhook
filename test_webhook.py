"""
Test script to simulate GitHub webhook events locally.
This script sends sample webhook payloads to the local webhook server
for development and testing purposes.
"""

import requests
import json
import hmac
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_github_webhook_secret").encode()

# Sample data for events
AUTHOR = "TestUser"
TARGET_BRANCH = "main"
SOURCE_BRANCH = "feature-branch"

def create_signature(payload):
    """Create a GitHub-compatible HMAC signature for the payload."""
    mac = hmac.new(WEBHOOK_SECRET, msg=payload.encode(), digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"

def send_webhook_event(event_type, payload):
    """Send a simulated webhook event to the local server."""
    payload_bytes = json.dumps(payload).encode()
    signature = create_signature(json.dumps(payload))
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": event_type,
        "User-Agent": "GitHub-Hookshot/test"
    }
    
    response = requests.post(WEBHOOK_URL, data=payload_bytes, headers=headers)
    
    print(f"Event: {event_type}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print("-" * 50)

def simulate_push_event():
    """Simulate a push event."""
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "ref": f"refs/heads/{TARGET_BRANCH}",
        "before": "0000000000000000000000000000000000000000",
        "after": "1234567890abcdef1234567890abcdef12345678",
        "repository": {
            "name": "action-repo",
            "full_name": "user/action-repo",
        },
        "pusher": {
            "name": AUTHOR,
            "email": f"{AUTHOR.lower()}@example.com"
        },
        "head_commit": {
            "id": "1234567890abcdef1234567890abcdef12345678",
            "message": "Test push commit",
            "timestamp": now
        }
    }
    
    send_webhook_event("push", payload)

def simulate_pull_request_event(action="opened"):
    """Simulate a pull request event with the specified action."""
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # For 'opened' action, merged should be false
    # For 'closed' action with merge, merged should be true
    merged = False
    if action == "closed":
        merged = True
    
    payload = {
        "action": action,
        "number": 42,
        "pull_request": {
            "url": "https://api.github.com/repos/user/action-repo/pulls/42",
            "id": 12345678,
            "number": 42,
            "state": "open" if action == "opened" else "closed",
            "title": "Test Pull Request",
            "user": {
                "login": AUTHOR
            },
            "body": "This is a test pull request",
            "created_at": now,
            "updated_at": now,
            "closed_at": now if action == "closed" else None,
            "merged_at": now if action == "closed" and merged else None,
            "merge_commit_sha": "abcdef1234567890abcdef1234567890abcdef12" if action == "closed" and merged else None,
            "merged": merged,
            "head": {
                "ref": SOURCE_BRANCH
            },
            "base": {
                "ref": TARGET_BRANCH
            }
        },
        "repository": {
            "name": "action-repo",
            "full_name": "user/action-repo",
        },
        "sender": {
            "login": AUTHOR
        }
    }
    
    send_webhook_event("pull_request", payload)

if __name__ == "__main__":
    print("GitHub Webhook Tester")
    print("=" * 50)
    
    while True:
        print("\nSelect an event to simulate:")
        print("1. Push Event")
        print("2. Pull Request Opened")
        print("3. Pull Request Merged")
        print("4. All Events (1, 2, 3 in sequence)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == "1":
            simulate_push_event()
        elif choice == "2":
            simulate_pull_request_event("opened")
        elif choice == "3":
            simulate_pull_request_event("closed")  # closed with merged=true
        elif choice == "4":
            simulate_push_event()
            simulate_pull_request_event("opened")
            simulate_pull_request_event("closed")
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
