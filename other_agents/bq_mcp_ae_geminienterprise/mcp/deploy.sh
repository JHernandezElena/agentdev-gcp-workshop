#!/bin/bash
set -e

# Configuration
SERVICE_NAME="toolbox"
SERVICE_ACCOUNT_NAME="toolbox-identity"
REGION="us-central1"
IMAGE="us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest"
TOOLS_FILE="mcp.yaml"
# Use defaults if not set
BIGQUERY_RUN_PROJECT_ID=YOUR-PROJECT-ID
BIGQUERY_DATA_PROJECT_ID=YOUR-PROJECT-ID
BIGQUERY_DATA_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID environment variable is not set."
  echo "Please set it using: export PROJECT_ID=your-project-id"
  exit 1
fi

echo "Deploying to project: $PROJECT_ID"

# 1. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com

# 2. Create Service Account
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" &>/dev/null; then
  echo "Creating service account: $SERVICE_ACCOUNT_NAME"
  gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME"
else
  echo "Service account $SERVICE_ACCOUNT_NAME already exists."
fi

# 3. Grant Permissions
echo "Granting permissions..."
# Secret Manager Access
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"

# 4. Create/Update Secret
echo "Uploading tools configuration to Secret Manager..."
if gcloud secrets describe tools &>/dev/null; then
  gcloud secrets versions add tools --data-file="$TOOLS_FILE"
else
  gcloud secrets create tools --data-file="$TOOLS_FILE"
fi

# 5. Deploy to Cloud Run
echo "Deploying to Cloud Run..."


gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --service-account "$SERVICE_ACCOUNT_NAME" \
  --region "$REGION" \
  --set-secrets "/app/$TOOLS_FILE=tools:latest" \
  --set-env-vars "BIGQUERY_RUN_PROJECT_ID=$BIGQUERY_RUN_PROJECT_ID,BIGQUERY_DATA_PROJECT_ID=$BIGQUERY_DATA_PROJECT_ID,BIGQUERY_DATA_LOCATION=$BIGQUERY_DATA_LOCATION" \
  --args="--tools-file=/app/$TOOLS_FILE","--address=0.0.0.0","--port=8080" 
  #  --allow-unauthenticated

echo "Deployment complete!"
