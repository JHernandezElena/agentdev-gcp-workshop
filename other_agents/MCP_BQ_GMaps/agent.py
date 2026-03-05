import os
from dotenv import load_dotenv

import google.auth
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams 

from google.adk.agents import LlmAgent

# Load environment variables
load_dotenv(override=True)
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
PROJECT_ID=os.getenv("PROJECT_ID")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")


MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp" 
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" 

def maps_mcp_toolset():
    load_dotenv()
    maps_api_key = os.getenv('MAPS_API_KEY', 'no_api_found')
    
    tools= MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MAPS_MCP_URL,
        headers={    
            "X-Goog-Api-Key": maps_api_key
        }
    )
)
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools


def bigquery_mcp_toolset():   
        
    credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/bigquery"]
    )

    credentials.refresh(google.auth.transport.requests.Request())
    oauth_token = credentials.token
        
    HEADERS_WITH_OAUTH = {
        "Authorization": f"Bearer {oauth_token}",
        "x-goog-user-project": project_id
    }

    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=HEADERS_WITH_OAUTH
        )
    )
    print("MCP Toolset configured for Streamable HTTP connection.")
    return tools

maps_toolset = maps_mcp_toolset()
bigquery_toolset = bigquery_mcp_toolset()

root_agent = LlmAgent(
    model=GEMINI_MODEL,
    name='root_agent',
    instruction=f"""
                Help the user answer questions by strategically combining insights from two sources:
                
                1.  **BigQuery toolset:** Access demographic (inc. foot traffic index), product pricing, and historical sales data in the  mcp_bakery dataset. Do not use any other dataset.
                Run all query jobs from project id: {PROJECT_ID}. 

                2.  **Maps Toolset:** Use this for real-world location analysis, finding competition/places and calculating necessary travel routes.
                    Include a hyperlink to an interactive map in your response where appropriate.
            """,
    tools=[maps_toolset, bigquery_toolset]
)