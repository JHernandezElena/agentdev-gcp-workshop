import asyncio
import vertexai
from vertexai import agent_engines

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

PROJECT_ID=os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
RESOURCE_NAME = os.getenv("RESOURCE_NAME")

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize the remote agent instance
remote_agent = agent_engines.get(RESOURCE_NAME)

# Query it
response = remote_agent.query(message="I need details on the coffee")
print(response)