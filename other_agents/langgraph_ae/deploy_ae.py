import os
import sys
import cloudpickle
from dotenv import load_dotenv

import agent 
from agent import SimpleLangGraphApp

import vertexai 
from vertexai import agent_engines

# --- FIX: no module found agent.py ---
# This tells cloudpickle: "Don't just reference 'agent', copy the actual code inside it."
# The deployment throughs an error but it stills work
cloudpickle.register_pickle_by_value(sys.modules['agent'])
# ----------------

# Load environment variables
load_dotenv(override=True)

MODEL=os.getenv("GEMINI_MODEL")
PROJECT_ID=os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET) 

app = SimpleLangGraphApp(project=PROJECT_ID, location=LOCATION)

# You could just paste this code in the agent.py file and it deployes without any errors
remote_agent = agent_engines.create(
    app,
    requirements=[
        "google-cloud-aiplatform[agent_engines,langchain]==1.137.0",
        "cloudpickle==3.0.0",
        "pydantic==2.11.2",
        "langgraph",
        "httpx",
    ],
    display_name="Agent Engine with LangGraph with Telemetry 3",
    # description="This is a sample custom application in Agent Engine that uses LangGraph",
    # Added for OTEL
    env_vars = {
                    "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
                    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
                },
)