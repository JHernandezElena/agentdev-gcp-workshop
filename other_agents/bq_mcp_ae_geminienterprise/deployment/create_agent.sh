#!/bin/bash

# --- Variables ---
PROJECT_ID="YOUR-PROJECT-ID" # Your Google Cloud Project ID
AUTHORIZATION_ID="bigquery-agent-auth" # A unique ID for the authorization, e.g., "gcal-agent-auth"
CLIENT_ID="YOUR-CLIENT-ID"
CLIENT_SECRET="YOUR-CLIENT-SECRET" # The OAuth 2.0 Client Secret from your Google Cloud project
SCOPES="https://www.googleapis.com/auth/bigquery" # A space-separated list of OAuth scopes, e.g., "https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/userinfo.email"
DISCOVERY_ENGINE_API_BASE_URL="https://discoveryengine.googleapis.com/v1alpha"

PROJECT_NUMBER="YOUR-PROJECT-NUMBER" # Your Google Cloud Project Number
LOCATION="YOUR-LOCATION" # The location of your resources, e.g., "us-central1"
AS_APP="YOUR-AS-APP" # The application identifier, e.g., "gcal-agent_1747246671415"
ASSISTANT_ID="default_assistant" # The assistant ID, e.g., "default_assistant"
AGENT_NAME="bigquery-agent" # A unique name for the agent, e.g., "gcal-agent-2"
AGENT_DISPLAY_NAME="BigQuery Agent" # The display name for the agent, e.g., "Google Calendar Agent"
AGENT_DESCRIPTION="BigQuery Agent" # A brief description of what the agent does
TOOL_DESCRIPTION="BigQuery Agent" # A description of the tool used by the agent
REASONING_ENGINE="YOUR-REASONING-ENGINE" # The full resource name of the reasoning engine, e.g., "projects/<PROJECT_NUMBER>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>"
AUTH_ID="bigquery-agent-auth" # The authorization ID, e.g., "gcal-agent-auth"
DISCOVERY_ENGINE_API_BASE_URL="https://discoveryengine.googleapis.com"

# --- Script Body ---
AUTH_TOKEN=$(gcloud auth print-access-token)

curl -X POST \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "${DISCOVERY_ENGINE_API_BASE_URL}/v1alpha/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines/${AS_APP}/assistants/${ASSISTANT_ID}/agents" \
  -d '{
    "name": "projects/'"${PROJECT_NUMBER}"'/locations/'"${LOCATION}"'/collections/default_collection/engines/'"${AS_APP}"'/assistants/'"${ASSISTANT_ID}"'/agents/'"${AGENT_NAME}"'",
    "displayName": "'"${AGENT_DISPLAY_NAME}"'",
    "description": "'"${AGENT_DESCRIPTION}"'",
    "adk_agent_definition": {
      "tool_settings": {
        "tool_description": "'"${TOOL_DESCRIPTION}"'"
      },
      "provisioned_reasoning_engine": {
        "reasoning_engine": "'"${REASONING_ENGINE}"'"
      },
      "authorizations": [
        "projects/'"${PROJECT_NUMBER}"'/locations/global/authorizations/'"${AUTH_ID}"'"
      ]
    }
  }'