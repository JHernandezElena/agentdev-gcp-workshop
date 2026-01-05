# First A2A Agent to Cloud Run and Registering with Gemini Enterprise

This guide provides a comprehensive walkthrough of deploying an A2A (Agent-to-Agent) enabled agent, built with the Google Agent Development Kit (ADK), to Google Cloud Run. You will also learn how to register your deployed agent with Gemini Enterprise to make it discoverable and usable by other agents.

## Introduction

This project provides a template for creating and deploying a powerful, Gemini-based agent that can communicate with other agents using the A2A protocol. By the end of this guide, you will have a publicly accessible agent running on Cloud Run, ready to be integrated into the A2A ecosystem.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Google Cloud SDK:** [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install).
*   **A Google Cloud Project:** You will need a project with billing enabled to deploy to Cloud Run.
*   **Authentication:** Log in to your Google Cloud account and set up application default credentials:
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```

## Project Structure

The `to_deploy` directory contains all the necessary files for deploying the agent:

*   `main.py`: The main entry point for the application. It initializes and runs the FastAPI web server.
*   `gemini_agent.py`: Contains the core logic and definition of the Gemini agent, including its system instructions and tools.
*   `agent_executor.py`: Handles the execution of agent tasks by interfacing with the Google Agent Development Kit (ADK).
*   `requirements.txt`: A list of all the Python dependencies required for the agent to run.
*   `Procfile`: Specifies the command to start the web server, used by Google Cloud Run during deployment.
*   `deploy.sh`: A shell script that automates the entire deployment process.

## The ADK Agent (`gemini_agent.py`)

The heart of our application is the `GeminiAgent` class in `gemini_agent.py`. This class inherits from the `LlmAgent` provided by the Google ADK, and it's where you define your agent's identity, capabilities, and tools.

### Agent Identity

The agent's identity is defined by its `name` and `description`. You can customize these to reflect your agent's purpose:

```python
class GeminiAgent(LlmAgent):
    """An agent powered by the Gemini model via Vertex AI."""

    # --- AGENT IDENTITY ---
    name: str = "gemini_agent"
    description: str = "A helpful assistant powered by Gemini."
```

### System Instructions

The `instructions` variable within the `__init__` method sets the agent's system prompt. This is where you can define the agent's personality, its role, and any constraints on its behavior.

```python
class GeminiAgent(LlmAgent):
    def __init__(self, **kwargs):
        # --- SET YOUR SYSTEM INSTRUCTIONS HERE ---
        instructions = """
        You are a helpful and friendly assistant. Your task is to answer user queries using puns, if a city is mentioned, answer in the language spoken there.

        You can use the weather tool to find the weather in a location.
        """
```

### Tools

The ADK allows you to extend your agent's capabilities by giving it tools. In this example, we have a `get_weather` function that the agent can call. You can add your own tools by defining a Python function and registering it in the `tools` list.

```python
# --- DEFINE YOUR TOOLS HERE ---
def get_weather(location: str) -> str:
    """Gets the weather for a given location."""
    # In a real scenario, you might call a weather API here.
    return f"The weather in {location} is sunny."

class GeminiAgent(LlmAgent):
    def __init__(self, **kwargs):
        # --- REGISTER YOUR TOOLS HERE ---
        tools = [
            get_weather
        ]
```

## The A2A Executor (`agent_executor.py`)

The `AdkAgentToA2AExecutor` class in `agent_executor.py` is the bridge between the A2A framework and your ADK agent. It implements the `AgentExecutor` interface from the A2A library and is responsible for handling incoming requests and invoking your agent.

The `execute` method is the core of this class. It performs the following steps:

1.  **Retrieves the user's query** from the `RequestContext`.
2.  **Manages the task lifecycle**, creating a new task if one doesn't exist.
3.  **Manages the session**, creating a new session if one doesn't exist.
4.  **Invokes the ADK Runner** by calling `self._runner.run_async()`, passing the user's query.
5.  **Streams the response** back to the A2A framework, updating the task with the final result.

This executor ensures that your ADK-based agent can seamlessly communicate within the A2A protocol.

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

## Project Architecture

*   `main.py`: FastAPI server entry point. Initializes the `AdkAgentToA2AExecutor` and serves the agent.
*   `gemini_agent.py`: Core agent logic. Inherits from `LlmAgent`. This is where you define system instructions, tools, and agent identity.
*   `agent_executor.py`: The adapter class that implements the A2A `AgentExecutor` interface, bridging the A2A protocol with the ADK's `runner.run_async()` method.
*   `deploy.sh`: A utility script that automates the `gcloud` build, push, and deploy workflow.
*   `Procfile`: Specifies the `gunicorn` command for Cloud Run execution.

## Customization

To customize your agent, modify `gemini_agent.py`:

*   **Identity:** Change the `name` and `description` class variables.
*   **System Prompt:** Update the `instructions` string within the `__init__` method.
*   **Tools:** Add your own Python functions and register them in the `tools` list. Ensure your functions have type hints and clear docstrings, as these are used by the model for tool-use decisions.

## API Registration and Authentication

### Agent Registration

The agent is registered against the Discovery Engine API. The `curl` command in the Quick Start section sends a JSON payload containing the agent's display name, description, and the `jsonAgentCard`.

The `jsonAgentCard` is the core of the A2A definition, containing the public URL of the Cloud Run service and other metadata necessary for agent-to-agent communication.

### Authentication

When an agent's `AGENT_URL` points to a `.run.app` domain, Gemini Enterprise automatically attempts to authenticate using IAM.

For this to succeed, the service account used by the Discovery Engine service (`service-PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com`) must be granted the `roles/run.invoker` role on your Cloud Run service. The Quick Start script handles this for you.

This provides a secure, tokenless authentication mechanism between the two Google Cloud services.

## Lifecycle Management

### Unregistering the Agent

To remove the agent from Gemini Enterprise, you need its `AGENT_ID`. Then, execute a `DELETE` request to the same API endpoint.

```bash
# Set the ID of the agent you want to remove
export AGENT_ID="your-agent-id"

curl -X DELETE \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_ID/locations/global/collections/default_collection/engines/$ENGINE_ID/assistants/default_assistant/agents/$AGENT_ID"
```

### Deleting the Service

To shut down the Cloud Run service entirely:

```bash
gcloud run services delete $SERVICE_NAME --project=$PROJECT_ID --region=$REGION
```

## Disclaimer

Important: The sample code provided is for demonstration purposes and illustrates the mechanics of the Agent-to-Agent (A2A) protocol. When building production applications, it is critical to treat any agent operating outside of your direct control as a potentially untrusted entity.

All data received from an external agent—including but not limited to its AgentCard, messages, artifacts, and task statuses—should be handled as untrusted input. For example, a malicious agent could provide an AgentCard containing crafted data in its fields (e.g., description, name, skills.description). If this data is used without sanitization to construct prompts for a Large Language Model (LLM), it could expose your application to prompt injection attacks.  Failure to properly validate and sanitize this data before use can introduce security vulnerabilities into your application.

Developers are responsible for implementing appropriate security measures, such as input validation and secure handling of credentials to protect their systems and users.
