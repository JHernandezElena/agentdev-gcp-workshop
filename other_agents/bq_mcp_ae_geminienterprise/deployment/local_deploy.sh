#!/bin/bash

# --- Variables ---
GOOGLE_CLOUD_PROJECT=YOUR-PROJECT-ID
BIGQUERY_RUN_PROJECT_ID=YOUR-PROJECT-ID
BIGQUERY_DATA_PROJECT_ID=YOUR-PROJECT-ID
STAGING_BUCKET=your-staging-bucket
export AUTH_ID="bigquery-agent-auth"
AGENT_DISPLAY_NAME="BigQuery Agent"
URL_MCP_TOOLSET="https://toolbox-YOUR-PROJECT-ID.us-central1.run.app"

PROJECT_ID="yogaproject-1508" # Your Google Cloud Project ID
AUTHORIZATION_ID="bigquery-agent-auth" # A unique ID for the authorization, e.g., "gcal-agent-auth"
CLIENT_ID="YOUR-CLIENT-ID"
CLIENT_SECRET="YOUR-CLIENT-SECRET" # The OAuth 2.0 Client Secret from your Google Cloud project
SCOPES="https://www.googleapis.com/auth/bigquery" # A space-separated list of OAuth scopes, e.g., "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/userinfo.email"
DISCOVERY_ENGINE_API_BASE_URL="https://discoveryengine.googleapis.com/v1alpha"

# Using printf %s to avoid issues with newline in variable expansion
ENCODED_SCOPES=$(printf %s "${SCOPES}" | sed 's/ /+/g') # More robust way to replace spaces with +

AUTHORIZATION_URI="https://accounts.google.com/o/oauth2/v2/auth?&scope=${ENCODED_SCOPES}&include_granted_scopes=true&response_type=code&access_type=offline&prompt=consent"

# --- Script Body ---
AUTH_TOKEN=$(gcloud auth print-access-token)
echo "Please set it using: export PROJECT_ID=your-project-id"
