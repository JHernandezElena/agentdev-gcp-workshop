import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

DATASTORE_PROJECT_ID = os.getenv("DATASTORE_PROJECT_ID")
DATASTORE_ID = os.getenv("DATASTORE_ID")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_LIVE_MODEL = os.getenv("GEMINI_LIVE_MODEL")
DATASTORE_LOCATION = os.getenv("DATASTORE_LOCATION")


# The full datastore path is constructed from the environment variables.
full_datastore_path = f"projects/{DATASTORE_PROJECT_ID}/locations/{DATASTORE_LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}"

# Tool Instantiation
vertex_search_tool = VertexAiSearchTool(data_store_id=full_datastore_path)

# Agent Definition
root_agent = LlmAgent(
    name="alphabet_earnings_search_agent",
    model=GEMINI_LIVE_MODEL,
    instruction="""You are a helpful assistant that uses the Vertex AI Search tool to answer questions.
          When a user asks a question, use the `vertex_ai_search` tool to find the answer.
          Output *only* the relevant information found by the tool.
          Always cite sources when available.
          """,
    description="Searches for information using Vertex AI Search.",
    tools=[vertex_search_tool],
    output_key="vertex_ai_search_results"
)

from google.adk.apps import App

app = App(root_agent=root_agent, name="app")
