import os
import sys
import cloudpickle
from dotenv import load_dotenv

import agent 
from agent import SimpleLangGraphApp

import vertexai 
from vertexai import agent_engines
from vertexai import types

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

client = vertexai.Client(project=PROJECT_ID, location=LOCATION, http_options=dict(api_version="v1beta1")) #v1beta1 API for agent identity support

app = SimpleLangGraphApp(project=PROJECT_ID, location=LOCATION)

# identity_type and agent_framework is only avaiable with this client.agent_engines.create method
remote_agent = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "Agent Engine with LangGraph with Identity and Telemetry",
        #"description": "This is a sample custom application in Agent Engine that uses LangGraph",
        "identity_type": types.IdentityType.AGENT_IDENTITY,
        #"service_account": "my-new-custom-service-account@my-project.iam.gserviceaccount.com",
        "requirements": [
                "google-cloud-aiplatform[agent_engines,langchain]==1.137.0",
                "cloudpickle==3.1.2",
                "pydantic==2.12.5",
                "langgraph",
                "httpx",
                "google-auth[cryptography]"
            ],
        "staging_bucket": STAGING_BUCKET,
        "agent_framework": "langgraph", 
        "env_vars": {
                    "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true",
                    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
                },
    }
)