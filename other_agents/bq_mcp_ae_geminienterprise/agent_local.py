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

"""Agent module for the bigquery bus stop images and information."""

from google.adk.agents import LlmAgent
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows
import json

from google.adk import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai import types
from google.genai.types import ThinkingConfig, HttpRetryOptions
from google.oauth2.credentials import Credentials
import google.auth
import google.auth.transport.requests
from google.adk.auth import AuthConfig
from google.adk.auth import AuthCredential
from google.adk.auth import AuthCredentialTypes
from google.adk.auth import OAuth2Auth
import vertexai
from vertexai import agent_engines

from googleapiclient.discovery import build
from .tools import get_latest_bus_stop_images, mcp_toolset, \
    data_project_id
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

# configure logging __name__
logger = logging.getLogger(__name__)
load_dotenv()

print("loading .env")

# Access the variable

oauth_client_id = os.getenv("OAUTH_CLIENT_ID")
oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")
google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
###
google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
staging_bucket = os.getenv("STAGING_BUCKET")
auth_id = os.getenv("AUTH_ID")
agent_display_name = os.getenv("AGENT_DISPLAY_NAME")
local_dev = os.getenv("LOCAL_DEV")

SCOPES = [os.getenv("SCOPES")]

def current_datetime(callback_context: CallbackContext):
  # get current date time
  now = datetime.now()
  formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
  callback_context.state["_time"] = formatted_time


def prereq_setup(callback_context: CallbackContext):
  print("**** PREREQ SETUP ****")
  if local_dev:
      creds, project = google.auth.default()
      auth_req = google.auth.transport.requests.Request()
      creds.refresh(auth_req)
      access_token = creds.token
      callback_context.state["auth_token"] = access_token
      print(f"Access token local: {access_token}")
  else:
    access_token = callback_context.state[f"temp:{auth_id}"]
    print(f"Access token remote: {access_token}")
  creds = Credentials(token=access_token)
  current_datetime(callback_context)

def auth_user(tool_context: ToolContext):
  creds = None
  # Check if the tokes were already in the session state, which means the user
  # has already gone through the OAuth flow and successfully authenticated and
  # authorized the tool to access their calendar.
  if "bq_tool_tokens" in tool_context.state:
    creds = Credentials.from_authorized_user_info(
        tool_context.state["bq_tool_tokens"], SCOPES
    )
    print(f"******** Tool contex state: {tool_context.state["bq_tool_tokens"]}")
  if not creds or not creds.valid:
    # If the access token is expired, refresh it with the refresh token.
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      auth_scheme = OAuth2(
          flows=OAuthFlows(
              authorizationCode=OAuthFlowAuthorizationCode(
                  authorizationUrl="https://accounts.google.com/o/oauth2/auth",
                  tokenUrl="https://oauth2.googleapis.com/token",
                  scopes={
                      "https://www.googleapis.com/auth/bigquery": (
                          "Query your BigQuery datasets"
                      ),
                      "https://www.googleapis.com/auth/userinfo.email": (
                          "View your email address"
                      )
                  },
              )
          )
      )
      auth_credential = AuthCredential(
          auth_type=AuthCredentialTypes.OAUTH2,
          oauth2=OAuth2Auth(
              client_id=oauth_client_id, client_secret=oauth_client_secret
          ),
      )
      # If the user has not gone through the OAuth flow before, or the refresh
      # token also expired, we need to ask users to go through the OAuth flow.
      # First we check whether the user has just gone through the OAuth flow and
      # Oauth response is just passed back.
      auth_response = tool_context.get_auth_response(
          AuthConfig(
              auth_scheme=auth_scheme, raw_auth_credential=auth_credential
          )
      )
      if auth_response:
        # ADK exchanged the access token already for us
        access_token = auth_response.oauth2.access_token
        refresh_token = auth_response.oauth2.refresh_token

        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri=auth_scheme.flows.authorizationCode.tokenUrl,
            client_id=oauth_client_id,
            client_secret=oauth_client_secret,
            scopes=list(auth_scheme.flows.authorizationCode.scopes.keys()),
        )
      else:
        # If there are no auth response which means the user has not gone
        # through the OAuth flow yet, we need to ask users to go through the
        # OAuth flow.
        tool_context.request_credential(
            AuthConfig(
                auth_scheme=auth_scheme,
                raw_auth_credential=auth_credential,
            )
        )
        # The return value is optional and could be any dict object. It will be
        # wrapped in a dict with key as 'result' and value as the return value
        # if the object returned is not a dict. This response will be passed
        # to LLM to generate a user friendly message. e.g. LLM will tell user:
        # "I need your authorization to access your data. Please authorize
        # me so I can check your data."
        return "Need User Authorization to access BQ. " \
               "Please allow pop-ups and go through the authorization process"

    # We store the access token and refresh token in the session state 
    print(f"Access token en auth tool: {access_token}")
    tool_context.state["bq_tool_tokens"] = json.loads(creds.to_json())

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
    planner=BuiltInPlanner(
        # "Thoughts" will be produced by the LLM and displayed in the UI
        thinking_config=ThinkingConfig(include_thoughts=True)),
    tools=[        
        # Custom tool defined in the agent
        get_latest_bus_stop_images #,
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
        checking and suggesting Bus Stop information.
        Greet the user by welcoming the user to the Bus Stop Helper, let the user know you'll need to authenticate to begin and authenticate the user 
        using auth_user. If user asks you to check bus stop information , please
        always use "bq_bus_stop_agent" to check bus stop results. Never greet user again if you already did previously.""",
    sub_agents=[bq_bus_stop_agent],
    tools=[auth_user],
    # flow="auto",
)