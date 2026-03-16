# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.§

### THIS IS THE AGENT VERSION OF THE BIGQUERY AGENT REGISTERED ON GEMINI ENTERPRISE ###

"""Agent module for the bigquery bus stop images and information."""

from google.adk.agents import LlmAgent
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import json

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai import types
from google.genai.types import ThinkingConfig, HttpRetryOptions

import vertexai
from vertexai import agent_engines


from googleapiclient.discovery import build
from tools import get_latest_bus_stop_images, mcp_toolset, \
    data_project_id
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

# configure logging __name__
logger = logging.getLogger(__name__)
load_dotenv()

print("loading .env")

###
google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
staging_bucket = os.getenv("STAGING_BUCKET")
auth_id = os.getenv("AUTH_ID")
agent_display_name = os.getenv("AGENT_DISPLAY_NAME")
url_mcp_toolset = os.getenv("URL_MCP_TOOLSET")
bigquery_run_project_id = os.getenv("BIGQUERY_RUN_PROJECT_ID")
data_project_id=os.getenv("BIGQUERY_DATA_PROJECT_ID")
bigquery_data_location = os.getenv("BIGQUERY_DATA_LOCATION")


def current_datetime(callback_context: CallbackContext):
  # get current date time
  now = datetime.now()
  formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
  callback_context.state["_time"] = formatted_time


def prereq_setup(callback_context: CallbackContext):
  print("**** PREREQ SETUP ****")
  current_state = callback_context.state.to_dict()
  # print all the values in the dict current_state
  for key, value in current_state.items():
    if key == auth_id:
      access_token = value
      print(f"EXACT MATCH AUTH ID in state: {key} : {value}")
    elif key.startswith(auth_id):
      print(f"STARTS WITH AUTH ID in state: {key} : {value}")
      access_token = value
    else:
      print(f"NOT AUTH ID KEY other key in state: {key} : {value}")
  
  #access_token = callback_context.state[f"{auth_id}"]
  print("***access_token***", access_token)
  #creds = Credentials(token=access_token)
  current_datetime(callback_context)

# While not important for this agent, can be critical for others
safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
]

# This config can fine tune the LLM responses
generate_content_config = types.GenerateContentConfig(
    safety_settings=safety_settings,
    temperature=0.1,
    max_output_tokens=3000,
    top_k=2,
    top_p=0.95,
)

# For production deployments these options should be provided via configuration
retry_options = HttpRetryOptions(
    attempts=10,
    initial_delay=10,
    max_delay=5000,
    exp_base=1.5,
    jitter=0.5
)

bq_bus_stop_agent = Agent(
    name="bigquery_interaction_demo_agent",
    generate_content_config=generate_content_config,
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_options
    ),
    description="Bus stop image analysis agent",
    instruction=
    f"""You can answer questions about bus stop images. You must use only the provided tools to answer the questions.
    
    If you use the ask-data-insights tool, make sure to provide the table_reference parameter exactly as
    "[{{"projectId": "{data_project_id}", "datasetId":"multimodal", "tableId": "image_reports"}}]. When showing the response of the ask-data-insights tool show the SQL statement provided in the tool return.
    
    If you use the get-table-information tool, make sure to provide the dataset parameter as "multimodal".
    
    If you are asked to describe your capabilities, reply with some variation on the following message. Use the tone of the question to generate the response.
    "I can answer questions about the bus stop images and about BigQuery tables in the multimodal dataset. Try asking these questions:
     - Show the bus stop images
     - Find images containing broken glass
     - What is the breakdown of bus stop cleanliness levels?
     - What tables are in the multimodal dataset?
     - Who has access to the multimodal dataset?
     - What is the schema of the image_reports table?
    "
    """,
    #planner=BuiltInPlanner(
        # "Thoughts" will be produced by the LLM and displayed in the UI
    #    thinking_config=ThinkingConfig(include_thoughts=True)),
    tools=[        
        # Custom tool defined in the agent
        get_latest_bus_stop_images,
        # A set of tools provided by a remote MCP server
        mcp_toolset
    ],
    before_agent_callback=prereq_setup,
)


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="root_agent",
    instruction="""
        You are a helpful virtual assistant for Google to help users by 
        checking and answering questions about Bus Stops.
        If user asks you to check bus stops images or ask questions about bus stops, please
        always use "bq_bus_stop_agent". Never greet user again if you already did previously.""",
    sub_agents=[bq_bus_stop_agent],
    # flow="auto",
)


def deploy_agent_engine_app():
  app = agent_engines.AdkApp(
    app_name="app",
    agent=root_agent,
    enable_tracing=True,
  )
 
  vertexai.init(
    project=google_cloud_project,  # Your project ID.
    location=google_cloud_location,  # Your cloud region.
    staging_bucket=staging_bucket,  # Your staging bucket.
  )

  requirements =  ['google-generativeai', 'uvicorn', 'python-dotenv', 'asyncclick', 'gunicorn', 'google-cloud-aiplatform>=1.126.1', 'google-adk>=1.19.0', 'toolbox_core', 'cloudpickle==3.1.2', 'pydantic==2.12.4']

  env_variables = {
    "AUTH_ID": auth_id,
    "AGENT_DISPLAY_NAME": agent_display_name,
    "DATA_PROJECT_ID": data_project_id,
    "URL_MCP_TOOLSET": url_mcp_toolset,
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
    "BIGQUERY_RUN_PROJECT_ID": bigquery_run_project_id,
    "BIGQUERY_DATA_PROJECT_ID": data_project_id
  } 

  agent_config = {
      "agent_engine": app,
      "display_name": agent_display_name,
      "requirements": requirements,
      "env_vars": env_variables,
      "extra_packages": ["./tools.py"]
  }


  existing_agents = list(
      agent_engines.list(filter=f'display_name="{agent_display_name}"'))

  if existing_agents:
    print(f"Number of existing agents found for {agent_display_name}:" + str(
        len(list(existing_agents))))
    print(existing_agents[0].resource_name)

  if existing_agents:
    # update the existing agent
    remote_app = agent_engines.update(
        resource_name=existing_agents[0].resource_name, **agent_config)
  else:
    # create a new agent
    remote_app = agent_engines.create(**agent_config)

  return None


if __name__ == "__main__":
  deploy_agent_engine_app()
