import os
from dotenv import load_dotenv

from agent import root_agent, bq_logging_plugin

import vertexai 
from vertexai import agent_engines

# Load environment variables
load_dotenv(override=True)

PROJECT_ID=os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET) 

app_to_deploy = agent_engines.AdkApp(
  agent=root_agent,
  plugins=[bq_logging_plugin]
  )

env_vars = {
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
        "MAPS_MCP_URL": os.getenv("MAPS_MCP_URL", ""),
        "MAPS_API_KEY": os.getenv("MAPS_API_KEY", ""),
        "DATASET_NAME": os.getenv("DATASET_NAME", ""),
        "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "")
}

agent_config = {
      "agent_engine": app_to_deploy,
      "display_name": "Baseline BQ Manufacturing Agent",
      "requirements": ["google-cloud-aiplatform[adk, agent_engines]==1.137.0", "google-adk==1.23.0"],
      "env_vars": env_vars,
  }

remote_app = agent_engines.create(**agent_config)