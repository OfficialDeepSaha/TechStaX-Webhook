import os
import hmac
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient, DESCENDING
from dotenv import load_dotenv
from bson.json_util import dumps, loads
import json
import uuid

load_dotenv()

app = Flask(__name__)

# MongoDB configuration
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")
webhook_secret = os.getenv("WEBHOOK_SECRET").encode() if os.getenv("WEBHOOK_SECRET") else b''

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

def verify_signature(payload):
    signature_header = request.headers.get('X-Hub-Signature-256')
    if not signature_header:
        return False
    
    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(webhook_secret, msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify signature
    payload = request.get_data()
    if not verify_signature(payload):
        return jsonify({"status": "error", "message": "Invalid signature"}), 401

    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json

    # Process different event types
    if event_type == 'push':
        process_push_event(payload)
    elif event_type == 'pull_request':
        process_pull_request_event(payload)
    
    return jsonify({"status": "success"}), 200

def process_push_event(payload):
    author = payload['pusher']['name']
    to_branch = payload['ref'].split('/')[-1]
    # Use the timestamp from the payload if available, otherwise use current time
    if 'head_commit' in payload and payload['head_commit'] and 'timestamp' in payload['head_commit']:
        timestamp = payload['head_commit']['timestamp']
    else:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    commit_hash = payload['after'] if 'after' in payload else payload.get('head_commit', {}).get('id', '')

    event_data = {
        "request_id": commit_hash,
        "author": author,
        "action": "PUSH",
        "from_branch": "",
        "to_branch": to_branch,
        "timestamp": timestamp
    }
    collection.insert_one(event_data)

def process_pull_request_event(payload):
    pr_payload = payload['pull_request']
    action_type = payload['action']
    
    if action_type == 'opened':
        event_type = "PULL_REQUEST"
    elif action_type == 'closed' and pr_payload['merged']:
        event_type = "MERGE"
    else:
        return
    
    author = pr_payload['user']['login']
    from_branch = pr_payload['head']['ref']
    to_branch = pr_payload['base']['ref']
    
    # Use the updated_at timestamp from the PR, which is in ISO format
    timestamp = pr_payload['updated_at']
    request_id = str(pr_payload['number'])

    event_data = {
        "request_id": request_id,
        "author": author,
        "action": event_type,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp
    }
    collection.insert_one(event_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/events')
def get_events():
    # Find all events, exclude the _id field, sort by timestamp in descending order
    limit = request.args.get('limit', default=20, type=int)
    skip = request.args.get('skip', default=0, type=int)
    action_filter = request.args.get('action', default=None, type=str)
    
    # Apply filters if provided
    query = {}
    if action_filter:
        query['action'] = action_filter.upper()
    
    events = list(collection.find(query, {'_id': 0}).sort('timestamp', DESCENDING).skip(skip).limit(limit))
    
    # Using dumps to handle MongoDB date objects
    return dumps(events)

@app.route('/api/stats')
def get_stats():
    # Get event counts by type
    total_count = collection.count_documents({})
    push_count = collection.count_documents({'action': 'PUSH'})
    pr_count = collection.count_documents({'action': 'PULL_REQUEST'})
    merge_count = collection.count_documents({'action': 'MERGE'})
    
    stats = {
        'total': total_count,
        'push': push_count,
        'pull_request': pr_count,
        'merge': merge_count
    }
    
    return jsonify(stats)

# Debug route to clear all events - useful during testing
@app.route('/api/clear', methods=['POST'])
def clear_events():
    if request.headers.get('X-Admin-Key') == os.getenv('ADMIN_KEY'):
        result = collection.delete_many({})
        return jsonify({
            "status": "success", 
            "message": f"All events cleared", 
            "count": result.deleted_count
        })
    return jsonify({"status": "error", "message": "Unauthorized"}), 401

@app.route('/api/simulate', methods=['POST'])
def simulate_event():
    """Endpoint to simulate webhook events for testing"""
    try:
        payload = request.json
        event_type = payload.get('type')
        
        if event_type == 'push':
            # Simulate push event
            author = payload.get('author', 'TestUser')
            to_branch = payload.get('to_branch', 'main')
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            event_data = {
                "request_id": str(uuid.uuid4())[:8],
                "author": author,
                "action": "PUSH",
                "from_branch": "",
                "to_branch": to_branch,
                "timestamp": timestamp
            }
            collection.insert_one(event_data)
            
        elif event_type == 'pull_request':
            # Simulate pull request event
            author = payload.get('author', 'TestUser')
            from_branch = payload.get('from_branch', 'feature')
            to_branch = payload.get('to_branch', 'main')
            action = payload.get('action', 'opened')
            merged = payload.get('merged', False)
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            if action == 'opened':
                event_type = "PULL_REQUEST"
            elif action == 'closed' and merged:
                event_type = "MERGE"
            else:
                return jsonify({"status": "error", "message": "Invalid action or merge state"})
            
            event_data = {
                "request_id": str(uuid.uuid4())[:8],
                "author": author,
                "action": event_type,
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp
            }
            collection.insert_one(event_data)
            
        else:
            return jsonify({"status": "error", "message": "Invalid event type"})
            
        return jsonify({"status": "success", "message": "Event simulated successfully"})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)