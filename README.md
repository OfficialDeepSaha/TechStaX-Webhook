# GitHub Webhook Monitoring System

This project implements a complete GitHub webhook monitoring system that captures and displays GitHub events (Push, Pull Request, and Merge) in real-time.

## Project Overview

The system consists of two repositories:

1. **action-repo**: The source repository that generates GitHub webhook events
2. **webhook-repo**: A Flask application that receives webhook events, stores them in MongoDB, and displays them in a real-time UI

The UI automatically refreshes every 15 seconds to show the latest GitHub activities in the format specified by the requirements.

## MongoDB Schema

The events are stored in MongoDB with the following schema:

| Field | Datatype | Details |
| ----- | -------- | ------- |
| id | ObjectID | MongoDB default ID |
| request_id | string | Use the Git commit hash directly. For Pull Requests, use the PR ID |
| author | string | Name of the GitHub user making that action |
| action | string | Name of the GitHub action: is an Enum of "PUSH", "PULL_REQUEST", "MERGE" |
| from_branch | string | Name of Git branch in LHS (From action) |
| to_branch | string | Name of Git branch in RHS (To action) |
| timestamp | string(datetime) | Must be a datetime formatted string (UTC) for the time of action |

## Event Display Formats

Events are displayed in the following formats:

- **PUSH**: `{author} pushed to {to_branch} on {timestamp}`
- **PULL_REQUEST**: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`
- **MERGE**: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`

## Setup Instructions

### 1. MongoDB Setup

1. Create a free MongoDB Atlas account at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster and database
3. Create a collection named `events`
4. Get your MongoDB connection string
5. Update the `.env` file in the webhook-repo with your MongoDB connection details

### 2. Webhook Repository Setup

```bash
cd webhook-repo

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit the .env file with your MongoDB connection string and webhook secret
```

### 3. Action Repository Setup

For deployment to GitHub:

1. Create a new GitHub repository named `action-repo`
2. Push your local `action-repo` directory to this repository:

```bash
cd action-repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/action-repo.git
git branch -M main
git push -u origin main
```

### 4. Webhook Configuration

1. In your GitHub `action-repo` settings, go to "Webhooks" and click "Add webhook"
2. Set the following:
   - Payload URL: Your webhook endpoint URL (e.g., `https://your-domain.com/webhook` or use a service like ngrok for local development)
   - Content type: `application/json`
   - Secret: Same as your `WEBHOOK_SECRET` in the `.env` file
   - Events: Select "Send me everything" or individually select "Push" and "Pull requests"
   - Active: Check this box

### 5. Run the Webhook Server

```bash
cd webhook-repo
python app.py
```

If you're developing locally, you can use [ngrok](https://ngrok.com/) to create a public URL:

```bash
ngrok http 5000
```

Then use the ngrok URL as your webhook payload URL in GitHub settings.

## Testing the Webhook Integration

### Test Push Events

1. Make a change to any file in the `action-repo`
2. Commit and push the changes:

```bash
git add .
git commit -m "Test push event"
git push origin main
```

### Test Pull Request and Merge Events

1. Create a new branch:

```bash
git checkout -b feature-branch
```

2. Make changes, commit, and push to the new branch:

```bash
git add .
git commit -m "Add feature"
git push origin feature-branch
```

3. Go to GitHub and create a Pull Request from `feature-branch` to `main`
4. Merge the Pull Request using GitHub's UI

## Viewing the Events

Open the webhook application in your browser:

- If running locally: `http://localhost:5000`
- If using ngrok: Use the ngrok URL

The UI will display all GitHub events with automatic refresh every 15 seconds.
