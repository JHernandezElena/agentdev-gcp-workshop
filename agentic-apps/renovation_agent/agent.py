import os
from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient
from google.genai import types
import warnings
import logging
# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")

print("--- DEBUG: DUMPING VARIABLES ---")
print(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
print(f"GOOGLE_CLOUD_LOCATION: {os.environ.get('GOOGLE_CLOUD_LOCATION')}")
print(f"GOOGLE_GENAI_USE_VERTEXAI: {os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")
print(f"STORAGE_BUCKET: {os.environ.get('STORAGE_BUCKET')}")
# Masking API Key for security locally, but showing if it exists
api_key = os.environ.get("GOOGLE_API_KEY")
print(f"GOOGLE_API_KEY: {'[SET]' if api_key else '[NOT SET]'}")
print("--- END DEBUG ---")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET")
GOOGLE_CLOUD_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")
GOOGLE_GENAI_USE_VERTEXAI = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI")

# Default to local toolbox if not set
TOOLBOX_ENDPOINT = os.environ.get("TOOLBOX_ENDPOINT", "http://127.0.0.1:5000")
print(f"Using TOOLBOX_ENDPOINT: {TOOLBOX_ENDPOINT}")

STAGING_BUCKET = "gs://" + STORAGE_BUCKET if STORAGE_BUCKET else None
ROOT_AGENT_NAME = "renovation_agent"
PROJECT_ID = GOOGLE_CLOUD_PROJECT
staging_bucket = STAGING_BUCKET
logger = logging.getLogger(__name__)

USER_ID = "user123"
SESSION_ID = "demo"
PROPOSAL_DOCUMENT_FILE_NAME =  "proposal_document_for_user.pdf"
MODEL_NAME = "gemini-2.0-flash"
from fastapi import HTTPException
toolbox = ToolboxSyncClient(TOOLBOX_ENDPOINT)
get_order_status_by_name = toolbox.load_tool('get-order-data')
get_orders_by_supplier_name = toolbox.load_tool('get-orders-by-supplier-name')


'''
# Root Agent Definition
'''
root_agent = Agent(
   model=MODEL_NAME,
   name=ROOT_AGENT_NAME,
   description=("Agent that finds order status for a material used in the building renovation for a home owner."),

# Instructions for intent detection: Combine guardrails string
# and the sub-agent routing instruction

   instruction=(
   """ 
    **********************************************************************************************************
    **********************************************************************************************************
    - If the user wants to know the status of order of a SPECIFIC MATERIAL or ITEM,
    then directly use the tool "get_order_status_by_name"
    to get the status of the object by contextually extracting the name of the material 
    from the user's input text. Remember the material name is used in direct comparison 
    in the database against the material_name field so make sure you extract the name 
    of the material for which the user is looking to find the status, correctly.
    
    - If the user wants to list orders for a SPECIFIC SUPPLIER,
    use the tool "get_orders_by_supplier_name" by extracting the supplier name.
    **********************************************************************************************************
    **********************************************************************************************************
   """),

    generate_content_config=types.GenerateContentConfig(temperature=0.2),


    tools = [
        get_order_status_by_name,
        get_orders_by_supplier_name
        ]
)
