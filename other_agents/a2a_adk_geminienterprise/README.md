# ADK Expense Reimbursement Agent

This sample uses the Agent Development Kit (ADK) to create a simple "Expense Reimbursement" agent that is hosted as an A2A server.

This agent takes text requests from the client and, if any details are missing, returns a webform for the client (or its user) to fill out. After the client fills out the form, the agent will complete the task.

## Prerequisites

- Python 3.9 or higher
- [UV](https://docs.astral.sh/uv/)
- Access to an LLM and API Key

## Running the Sample

1. Navigate to the samples directory:

    ```bash
    cd samples/python/agents/adk_expense_reimbursement
    ```

2. Create an environment file with your API key:

   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. Run an agent:

    ```bash
    uv run .
    ```

4. In a separate terminal, run the A2A client:

    ```bash
    # Connect to the agent (specify the agent URL with correct port)
    cd samples/python/hosts/cli
    uv run . --agent http://localhost:10002

    # If you changed the port when starting the agent, use that port instead
    # uv run . --agent http://localhost:YOUR_PORT


## Deployment

The `deploy.sh` script automates the deployment process. To deploy your agent, navigate to the `to_deploy` directory and run the script with your Google Cloud Project ID and a name for your new service. You can also optionally specify the Gemini model to use.

```bash
# --- Configuration ---
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1" # Or your preferred GCP region
export SERVICE_NAME="my-a2a-agent"
export ENGINE_ID="your-discovery-engine-id"

# --- 1. Deploy to Cloud Run ---
# This script builds the container, pushes it to GCR, and deploys to Cloud Run.
# It also updates the service with the required AGENT_URL environment variable.
bash deploy.sh $PROJECT_ID $SERVICE_NAME

# --- 2. Grant Invoker Permissions ---
# Allow Gemini Enterprise to securely call your agent via IAM.
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --project=$PROJECT_ID \
  --region=$REGION

# Or grant the  "Cloud Run Invoker" role to the following principal in the project where Cloud Run is running: `service-PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com`

gcloud projects add-iam-policy-binding yogaproject-1508 \
    --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-discoveryengine.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# --- 3. Register with Gemini Enterprise ---
# Define agent metadata
export AGENT_DISPLAY_NAME="My A2A Agent"
export AGENT_DESCRIPTION="A custom agent for backend processing."
export SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --project=$PROJECT_ID --region=$REGION --format='value(status.url)')

# Register via the Discovery Engine API
curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-Type: application/json" https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT_NUMBER/locations/LOCATION/collections/default_collection/engines/ENGINE_ID/assistants/default_assistant/agents -d '{
  "name": "AGENT_NAME",
  "displayName": "AGENT_DISPLAY_NAME",
  "description": "AGENT_DESCRIPTION",
    "a2aAgentDefinition": {
    "jsonAgentCard": "{\n         \"protocolVersion\":\"v1.0\",\n         \"version\":\"1.0.0\",\n         \"url\":\"SERVICE_URL\",\n         \"name\":\"AGENT_DISPLAY_NAME\",\n         \"description\":\"AGENT_DESCRIPTION\",\n         \"capabilities\":{},\n         \"defaultInputModes\": [\n           \"text/plain\"\n         ],\n         \"defaultOutputModes\": [\n           \"text/plain\"\n         ],\n         \"skills\":[\n            {\n             \"description\":\"SKILL_DESCRIPTION\",\n             \"id\":\"skill-123\",\n             \"name\":\"skill-123\",\n             \"tags\": []\n            }\n          ]\n       }"
   }
  }'
```

## Disclaimer

Important: The sample code provided is for demonstration purposes and illustrates the mechanics of the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

All data received from an external agent—including but not limited to its AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input. For example, a malicious agent could provide an AgentCard containing crafted data in its fields (e.g., description, name, skills.description). If this data is used without sanitization to construct prompts for a Large Language Model (LLM), it could expose your application to prompt injection attacks.  Failure to properly validate and sanitize this data before use can introduce security vulnerabilities into your application.

Developers are responsible for implementing appropriate security measures, such as input validation and secure handling of credentials to protect their systems and users.
