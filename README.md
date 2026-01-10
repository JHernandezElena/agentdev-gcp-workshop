# Agent Development Kit (ADK) Workshop & Examples

This repository contains a collection of AI agents and examples demonstrating the capabilities of the **Google Cloud Agent Development Kit (ADK)** and integration with **Vertex AI**.

The project features various implementation patterns including **OpenAPI** tool usage, **Model Context Protocol (MCP)**, **Agent-to-Agent (A2A)** communication, and deployment to **Vertex AI Agent Engine**.

## 📂 Project Structure

| Directory | Description | Key Features |
|-----------|-------------|--------------|
| **`petstore_agent/`** | A virtual Pet Store assistant. | • **OpenAPI Tools**: Generates tools from an OpenAPI spec.<br>• **Cloud Run**: Includes a mock backend service (`cloudrun-function`). |
| **`calcula_agent/`** | A calculation assistant. | • **MCP**: Demonstrates using the Model Context Protocol.<br>• **StreamableHTTP**: Shows specific connection parameters. |
| **`a2a_client_agent/`** | Client agent for A2A communication. | • **Agent-to-Agent**: Delegates queries to a remote agent.<br>• **Delegation**: Logic to route specific topics (e.g., earnings) to sub-agents. |
| **`alphabet_earnings_agent/`** | The remote service agent. | • **Remote Service**: Acts as the specialized agent answering earnings questions. |
| **`complex_multiagent/`** | Deployment examples. | • **Vertex AI Agent Engine**: Scripts (`deploy_ae.py`) to deploy multi-agent systems to Google Cloud. |
| **`weather_agent/`** | Simple introductory agent. | • Basic agent setup and structure. |
| **`code_writer_agent/`** | Specialized coding agent. | • Example of a specialized task agent. |
| **`other_agents/`** | Advanced & Miscellaneous samples. | • **HITL**: Human-in-the-Loop examples.<br>• **Model Armor**: Security/safety features.<br>• **Multimodal**: Agents handling non-text modalities. |

## 🚀 Getting Started

### 1. Prerequisites

*   Python 3.10+
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`) installed and authorized.
*   A Google Cloud Project with Vertex AI API enabled.

### 2. Installation

It is recommended to use a virtual environment to manage dependencies.

1.  **Create and Activate a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    Install the required Python packages from the root directory:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

Each agent directory typically contains its own `.env` file for configuration. You will need to set up environment variables for your specific GCP environment.

**Common Variables:**
*   `GEMINI_MODEL`: The model version to use (e.g., `gemini-1.5-pro-002`, `gemini-2.0-flash-exp`).
*   `PROJECT_ID`: Your Google Cloud Project ID.
*   `LOCATION`: GCP Region (e.g., `us-central1`).

**Example Setup:**
```bash
cd weather_agent
# Edit .env file
# GEMINI_MODEL=gemini-2.5-flash
# PROJECT_ID=my-gcp-project
```

### 4. Running Agents

Usage depends on the specific agent.

**For Vertex AI Deployment (e.g., `complex_multiagent`):**
Use the provided deployment scripts:
```bash
cd complex_multiagent
python deploy_ae.py
```

**For Local Development:**
Most agents define a `root_agent` object in `agent.py`. These can be run using standard ADK runners or by creating a simple entry script using `google.adk.run_agent`.

## 📚 Dependencies

Key libraries used in this project:
*   `google-adk`: Core Agent Development Kit.
*   `google-cloud-aiplatform`: Vertex AI SDK.
*   `fastapi` / `fastmcp`: For serving agents and MCP tools.
*   `pydantic`: Data validation.

## 🤝 Contributing

This is a workshop repository. Feel free to explore, modify, and create your own agents based on these patterns!
