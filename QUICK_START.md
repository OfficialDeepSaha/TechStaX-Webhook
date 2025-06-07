# GitHub Webhook Monitor - Quick Start Guide

This guide will help you quickly set up and run the GitHub webhook monitoring application for local development and testing.

## Local Development Setup

### 1. Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure MongoDB

#### Option A: Use Docker (Recommended)

The easiest way to run MongoDB locally is using Docker:

```bash
docker run --name mongodb -p 27017:27017 -d mongo:latest
```

#### Option B: MongoDB Atlas

Alternatively, create a free MongoDB Atlas account and update the `.env` file with your connection string.

### 3. Configure Environment Variables

Edit the `.env` file with your MongoDB connection details:

```
MONGO_URI="mongodb://localhost:27017/"
DB_NAME="github_events"
COLLECTION_NAME="events"
WEBHOOK_SECRET="your_github_webhook_secret"
ADMIN_KEY="your_admin_key_here"
PORT=5000
```

### 4. Initialize Database

Run the database initialization script to set up the MongoDB collection with the proper schema:

```bash
python init_db.py
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at http://localhost:5000

## Testing Without GitHub

You can test the application without setting up GitHub webhooks using either:

### Option 1: Admin Dashboard

1. Navigate to http://localhost:5000/admin
2. Use the "Test Webhook" form at the bottom of the page to simulate events

### Option 2: CLI Test Script

Run the included test script to simulate webhook events from the command line:

```bash
python test_webhook.py
```

## Exposing Local Server to the Internet

If you want to test with real GitHub webhooks, you need to make your local server accessible from the internet. Use ngrok:

```bash
# Install ngrok if you haven't already
# Then run:
ngrok http 5000
```

Use the generated ngrok URL as your GitHub webhook URL.

## Docker Compose Setup

For a complete development environment including MongoDB, use Docker Compose:

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down
```

This will start both MongoDB and the webhook application containers.

## Next Steps

Once you've verified the application is working locally, refer to the main README.md for:

1. Setting up the GitHub repositories
2. Configuring GitHub webhooks
3. Deploying to production
