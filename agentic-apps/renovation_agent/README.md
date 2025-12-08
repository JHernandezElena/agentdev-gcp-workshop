# Renovation Agent (ADK + MCP Toolbox)

> Based on the Codelab: [Build a Multi-agent App with MCP Toolbox for AlloyDB & ADK](https://codelabs.developers.google.com/multi-agent-app-toolbox-adk?hl=en#0)

This project implements a multi-agent system for a kitchen renovation project using the **Google Cloud Agent Development Kit (ADK)** and **MCP Toolbox for Databases**.

It demonstrates how to connect an AI agent to an **AlloyDB** database using the **Model Context Protocol (MCP)** to retrieve order status information.

## 🏗️ Architecture

1.  **Renovation Agent**: The core logic (built with ADK).
2.  **MCP Toolbox**: A middleware that creates standardized tools for database interaction.
3.  **AlloyDB**: The backend database storing material order statuses.
## ✅ Requirements Checklist

For this demo to work properly, ensure the following requirements are met:

### **Google Cloud Console Requirements**
- [ ] **Project:** A Google Cloud Project is created and Billing is enabled.
- [ ] **APIs Enabled:**
    - `artifactregistry.googleapis.com`
    - `cloudbuild.googleapis.com`
    - `run.googleapis.com`
    - `aiplatform.googleapis.com`
    - `alloydb.googleapis.com`
- [ ] **AlloyDB Cluster:** A cluster named `vector-cluster` and instance `primary` (or matching `tools.yaml`) exist.
- [ ] **Database:** A database named `postgres` exists in the instance.
- [ ] **Schema & Data:** The `material_order_status` table exists and contains sample data.
- [ ] **Credentials:** You have the password for the `postgres` user.

### **Local Development Server Requirements**
- [ ] **Python:** Python 3.9+ is installed.
- [ ] **Virtual Environment:** Active (`source .venv/bin/activate`).
- [ ] **Dependencies:** Installed via `pip install -r renovation_agent/requirements.txt`.
- [ ] **Configuration (.env):**
    - `GOOGLE_API_KEY` (Gemini API Key)
    - `GOOGLE_CLOUD_PROJECT`
    - `GOOGLE_CLOUD_LOCATION` (e.g., `us-central1`)
    - `STORAGE_BUCKET`
- [ ] **Configuration (tools.yaml):**
    - `project`, `region`, `cluster`, `instance`, `database`, `user`, `password` match your AlloyDB resources.
- [ ] **MCP Toolbox:** Running locally on port 5000 (`./toolbox --tools-file "tools.yaml"`).
- [ ] **ADK Agent:** Running locally on port 8000 (`adk web`).

## 🛠️ Setup Instructions

### 1. Prerequisites

*   Google Cloud Project with Billing Enabled.
*   APIs Enabled:
    *   `artifactregistry.googleapis.com`
    *   `cloudbuild.googleapis.com`
    *   `run.googleapis.com`
    *   `aiplatform.googleapis.com`
    *   `alloydb.googleapis.com`
*   Python 3.9+

### 2. Environment Setup

This project uses a `.env` file for configuration. Ensure the following variables are set:

```ini
GOOGLE_API_KEY=your_api_key
STORAGE_BUCKET=your_bucket_name
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

### 3. Database Setup (AlloyDB)

The project expects an AlloyDB cluster and instance with a `material_order_status` table.
*   **Cluster**: `vector-cluster`
*   **Instance**: `vector-instance`
*   **Database**: `postgres` (or as configured)

### 4. MCP Toolbox

The MCP Toolbox must be installed and running (either locally or on Cloud Run).

**To install the server:**
```bash
# See releases page for other versions
export VERSION=0.22.0
curl -L -o toolbox https://storage.googleapis.com/genai-toolbox/v$VERSION/linux/amd64/toolbox
chmod +x toolbox
```

**To run the server locally:**
```bash
./toolbox --tools-file "tools.yaml"
```

*   **Remote**: Update `agent.py` with the Cloud Run URL.

## 🚀 Running the Agent

1.  **Install Dependencies**:
    ```bash
    # Bug in pip resolver
    pip install -r renovation_agent/requirements.txt  --use-deprecated=legacy-resolver
    ```

2.  **Run with ADK**:
    ```bash
    adk run .
    ```

## 📂 Key Files

*   `agent.py`: Defines the ADK agent, tools, and prompts.
*   `tools.yaml`: Configuration for the MCP Toolbox (mapping SQL queries to tools).
*   `requirements.txt`: Python dependencies.
