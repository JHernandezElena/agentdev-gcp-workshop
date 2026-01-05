# BigQuery Bus Stop Images MCP Agent

This directory contains the configuration for a Model Context Protocol (MCP) agent designed to interact with a BigQuery dataset containing bus stop images. It uses the `toolbox` executable to serve the agent.
The based agent repository can be found here: [ADK and BigQuery](https://github.com/GoogleCloudPlatform/data-to-ai/blob/main/labs/agents/ADK-and-BigQuery.md)

## Overview

The agent provides tools to:
-   Search for bus stops by description using BigQuery SQL.
-   Perform conversational data analysis on the dataset.
-   Retrieve metadata about datasets and tables.

## Prerequisites

-   **Toolbox Executable**: The `toolbox` binary must be present in this directory and have execution permissions.
    ```bash
    chmod +x toolbox
    ```
-   **Google Cloud Credentials**: You need valid Google Cloud credentials to access the BigQuery datasets.
    ```bash
    gcloud auth application-default login
    ```

## Configuration

### Environment Variables

The `mcp.yaml` configuration file relies on the following environment variables. You must set these before running the agent:

-   `BIGQUERY_RUN_PROJECT_ID`: The Google Cloud Project ID where the BigQuery jobs will run.
-   `BIGQUERY_DATA_LOCATION`: The location of your BigQuery data (e.g., `US`, `EU`).
-   `BIGQUERY_DATA_PROJECT_ID`: The Google Cloud Project ID where the data resides (specifically for the `search-bus-stops-by-words-in-description` tool).

### MCP Configuration (`mcp.yaml`)

The `mcp.yaml` file defines the agent's capabilities. It includes:
-   **Source**: Defines the BigQuery connection.
-   **Tools**:
    -   `search-bus-stops-by-words-in-description`: Executes a SQL query to find bus stops.
    -   `ask-data-insights`: Uses Conversation Analytics API.
    -   `get-dataset-information`, `list-tables`, `get-table-information`: Metadata tools.

## Usage

To start the MCP agent locally, run the following command:

```bash
./toolbox --tools-file mcp.yaml
```

### Optional Flags

-   `--port <int>`: Specify the port the server will listen on (default: 5000).
-   `--log-level <level>`: Set logging level (DEBUG, INFO, WARN, ERROR).
-   `--ui`: Launch the Toolbox UI web server.

## Deploy to Cloud Run

You can deploy the MCP agent to Google Cloud Run using the provided `deploy.sh` script.

### Prerequisites for Deployment

1.  **Google Cloud Project**: You need an active Google Cloud Project.
2.  **Permissions**: You must have the following IAM roles on the project:
    -   `roles/iam.serviceAccountCreator`
    -   `roles/secretmanager.admin`
    -   `roles/run.developer`
3.  **Google Cloud CLI**: Ensure `gcloud` is installed and initialized.

### Automated Deployment

1.  Set your Project ID:
    ```bash
    export PROJECT_ID=your-project-id
    ```

2.  (Optional) Set BigQuery configuration if different from defaults:
    ```bash
    export BIGQUERY_RUN_PROJECT_ID=your-run-project # Defaults to PROJECT_ID
    export BIGQUERY_DATA_PROJECT_ID=your-data-project # Defaults to PROJECT_ID
    export BIGQUERY_DATA_LOCATION=US # Defaults to US
    ```

3.  Run the deployment script:
    ```bash
    ./deploy.sh
    ```

This script will automatically:
-   Enable necessary APIs (Cloud Run, Cloud Build, Artifact Registry, IAM, Secret Manager).
-   Create a service account (`toolbox-identity`) if it doesn't exist.
-   Grant the service account access to Secret Manager.
-   Upload your `mcp.yaml` configuration to Secret Manager.
-   Deploy the `toolbox` container to Cloud Run with the configuration mounted.

### Manual Deployment Steps

If you prefer to deploy manually, follow these steps (based on the [official guide](https://googleapis.github.io/genai-toolbox/how-to/deploy_toolbox/)):

1.  **Create Service Account**:
    ```bash
    gcloud iam service-accounts create toolbox-identity
    ```

2.  **Grant Permissions**:
    ```bash
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member serviceAccount:toolbox-identity@$PROJECT_ID.iam.gserviceaccount.com \
        --role roles/secretmanager.secretAccessor
    ```

3.  **Upload Configuration**:
    ```bash
    gcloud secrets create tools --data-file=mcp.yaml
    ```

4.  **Deploy**:
    ```bash
    export IMAGE=us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest
    gcloud run deploy toolbox \
        --image $IMAGE \
        --service-account toolbox-identity \
        --region us-central1 \
        --set-secrets "/app/$TOOLS_FILE=tools:latest" \
        --args="--tools-file=/app/$TOOLS_FILE","--address=0.0.0.0","--port=8080" \
        --allow-unauthenticated
