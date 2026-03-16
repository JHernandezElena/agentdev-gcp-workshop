import os
import logging
import dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
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
GRAPH_NAME = os.getenv("GRAPH_NAME")


def get_agent_prompt() -> str:
    return f"""You are an expert BigQuery Data Agent specialized in Graph Analytics.
                 Your primary capability is answering complex user questions by querying data stored in BigQuery.
                 
                 You differentiate yourself by preferring **GQL (Graph Query Language)** and **SQL/PGQ (Property Graph Query)**
                  syntax over traditional complex JOINs when traversing relationships.
                 
                    **Environment & Access:**
                    * **Project:** `{GOOGLE_CLOUD_PROJECT}`                    
                    * **Dataset:** `{DATASET_NAME}`
                    * **Graph Name:** `{GRAPH_NAME}`
                   
                    **Few-Shot Examples (GQL):**
                    
                    Example 1: Find all parts and materials for a product (Schema: Product -> Part -> Material)
                    GRAPH `kg_demo.manufacturing_kg`
                    MATCH (p:Product)-[e]->(pt:Part)-[c]->(m:Material)
                    RETURN
                      TO_JSON(p) AS product,
                      TO_JSON(e) AS contains_part,
                      TO_JSON(pt) AS part,
                      TO_JSON(c) AS made_of,
                      TO_JSON(m) AS material

                    Example 2: Find customers who purchased products with specific material (Schema: Customer -> Product -> Part -> Material)
                    GRAPH `kg_demo.manufacturing_kg`
                    MATCH (c:Customer)-[r]->(p:Product)-[e]->(pt:Part)-[f]->(m:Material {{material_id:"Fiberglass"}})
                    RETURN
                      TO_JSON(c) AS customer,
                      TO_JSON(r) AS purchased,
                      TO_JSON(p) AS product,
                      TO_JSON(e) AS contains_part,
                      TO_JSON(pt) AS part,
                      TO_JSON(f) AS made_of,
                      TO_JSON(m) AS material
                    LIMIT 100

                    You also have access to the Google Maps toolset.
                    If a Google Maps link is available, include it as a hyperlink on an appropriate word/phrase in the response so the user can click on it.

                    """

def create_graph_agent(model_name: str = GEMINI_MODEL) -> LlmAgent:
    """Creates and configures the Graph Agent with necessary tools."""
 
    bq_toolset = BigQueryToolset(
        tool_filter=['list_table_ids', 'get_table_info', 'execute_sql', 'get_dataset_info'] 
    )

    tools = [bq_toolset]

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

    agent_prompt = get_agent_prompt()

    return LlmAgent(
        name='knowledge_bq_agent',
        model=model_name,        
        instruction=agent_prompt,
        tools=tools
    )

# Required for adk web ui / adk run cli bindings
root_agent = create_graph_agent()

# Initialize the BigQuery Analytics Plugin
bq_config = BigQueryLoggerConfig(
    enabled=True,
    batch_size=1,
    shutdown_timeout=10.0
)

bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=GOOGLE_CLOUD_PROJECT,
    dataset_id="adk_bqplugging_analytics",
    table_id="manufacturingkg_agent_events", 
    config=bq_config,
    location=GOOGLE_CLOUD_LOCATION
)

# App wrapper is required to register the plugin
app = App(
    name="graphrag_BQ_manifacturing_agent", 
    root_agent=root_agent,
    plugins=[bq_logging_plugin]
)