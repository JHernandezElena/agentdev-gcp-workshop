import os
import logging
import dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig

logger = logging.getLogger(__name__)
env_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(env_path)

MAPS_MCP_URL = os.getenv("MAPS_MCP_URL")
MAPS_API_KEY = os.getenv("MAPS_API_KEY")

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
DATASET_NAME = os.getenv("DATASET_NAME")

# Ensure environment variables are set before ADK initialization
os.environ['GOOGLE_CLOUD_PROJECT'] = GOOGLE_CLOUD_PROJECT
os.environ['GOOGLE_CLOUD_LOCATION'] = GOOGLE_CLOUD_LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

def get_agent_prompt() -> str:
    return f"""You are an expert BigQuery Data Agent.
                 Your primary capability is answering complex user questions by querying data stored in BigQuery.
                 
                 You must use standard SQL (NL2SQL) against the tables in the BigQuery dataset. Do NOT use Graph Query Language (GQL).
                 
                    **Environment & Access:**
                    * **Project:** `{GOOGLE_CLOUD_PROJECT}`                    
                    * **Dataset:** `{DATASET_NAME}`
                   
                    **Instructions:**
                    - Write valid BigQuery SQL queries.
                    - Inspect the tables available in the dataset `{DATASET_NAME}` to find the relevant schema.
                    - Perform JOINs as needed to traverse relationships between tables (e.g., Product, Part, Material, Customer).
                    - Return the query results in a clear and concise format.

                    You also have access to the Google Maps toolset.
                    If a Google Maps link is available, include it as a hyperlink on an appropriate word/phrase in the response so the user can click on it.
                    """

def create_baseline_agent(model_name: str = GEMINI_MODEL) -> LlmAgent:
    """Creates and configures the Baseline NL2SQL Agent with necessary tools."""

    # Setup BigQuery Toolset    
    bq_toolset = BigQueryToolset(
        tool_filter=['list_table_ids', 'get_table_info', 'execute_sql', 'get_dataset_info'] 
    )

    tools = [bq_toolset]

    # Setup Maps Toolset Dynamically via Secret Manager
    maps_api_key = MAPS_API_KEY
    if not maps_api_key:
        logger.warning("MAPS_API_KEY effectively not found. Maps tool excluded from ADK.")
    else:
        maps_toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MAPS_MCP_URL,
                headers={"X-Goog-Api-Key": maps_api_key},
            ), 
            errlog=None
        )
        tools.append(maps_toolset)

    # Create Agent
    agent_prompt = get_agent_prompt()

    return LlmAgent(
        name='knowledge_bq_agent_baseline',
        model=model_name,        
        instruction=agent_prompt,
        tools=tools
    )

root_agent = create_baseline_agent()

# Initialize the BigQuery Analytics Plugin
bq_config = BigQueryLoggerConfig(
    enabled=True,
    batch_size=1,
    shutdown_timeout=10.0
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=GOOGLE_CLOUD_PROJECT,
    dataset_id="adk_bqplugging_analytics",
    table_id="manufacturingbaseline_agent_events", 
    config=bq_config,
    location=GOOGLE_CLOUD_LOCATION
)


# App wrapper is required to register the plugin
app = App(
    name="baseline_BQ_manifacturing_agent", 
    root_agent=root_agent,
    plugins=[bq_logging_plugin]
)

