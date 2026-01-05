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
# limitations under the License.
# add docstring to this module

"""Tools module for the maintenance scheduling agent."""

import logging
import os
from typing import List

from google.cloud import bigquery
from google.cloud.bigquery.enums import JobCreationMode
from google.cloud.bigquery.job import QueryJobConfig
from pydantic import BaseModel, Field
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.auth.credentials import Credentials
from toolbox_core import ToolboxClient, auth_methods
from dotenv import load_dotenv
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext



logger = logging.getLogger(__name__)
load_dotenv()

print("loading .env")

google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
data_project_id=os.getenv("BIGQUERY_DATA_PROJECT_ID")
url_mcp_toolset = os.getenv("URL_MCP_TOOLSET")


class BusStop(BaseModel):
    """
      Represents an analyzed image of a bus stop.
    """
    bus_stop_id: str = Field(description="Bus stop id")
    image_url: str = Field(description="Image URL")
    image_mime_type: str = Field(description="Image mime")
    cleanliness_level: int = Field(description="Cleanliness level")
    safety_level: int = Field(description="Safety level")
    description: str = Field(description="Description of the bus stop")

async def get_latest_bus_stop_images(number_of_images: int) -> List[BusStop]:
    logger = logging.getLogger(__name__)
    logger.info("*****Getting the list of bus stops*****")
    
    # Instantiate client here to avoid pickling issues during deployment
    bigquery_client = bigquery.Client(
        default_job_creation_mode=JobCreationMode.JOB_CREATION_OPTIONAL
    )
    
    bus_stops = []
    try:
        rows = bigquery_client.query_and_wait(
            project=os.getenv("BIGQUERY_RUN_PROJECT_ID"),
            job_config=QueryJobConfig(
                job_timeout_ms=60 * 1000
            ),
            query=f"""
            SELECT bus_stop_id, cleanliness_level, safety_level,
                uri as image_url, 'image/jpeg' as image_mime_type,
                description
            FROM `{data_project_id}.multimodal.image_reports`
            WHERE description != '' 
            ORDER BY updated DESC
            LIMIT {number_of_images}
            """
        )

        for row in rows:
            bus_stops.append(BusStop(
                bus_stop_id=row.bus_stop_id,
                image_url=row.image_url.replace("gs://",
                                    "https://storage.mtls.cloud.google.com/"),
                image_mime_type=row.image_mime_type,
                cleanliness_level=row.cleanliness_level,
                safety_level=row.safety_level,
                description=row.description
            ))
    except Exception as ex:
        logger.error("Call to retrieve bus stops failed: %s", str(ex))
        return {
            "status": "error"
        }

    logger.info("Retrieved bus stops: %s", bus_stops)
    return {
        "status": "success",
        "bus_stops": bus_stops
    }

def get_id_token():
  # Use synchronous method for token retrieval
  access_token = auth_methods.get_google_id_token(url_mcp_toolset)
  return access_token

class PicklableMcpToolset(McpToolset):
    def __init__(self, url, get_token_func):
        self._url = url
        self._get_token_func = get_token_func
        token = get_token_func()
        super().__init__(
            connection_params=  StreamableHTTPConnectionParams(
                url=url,
                headers={"Authorization": f"Bearer {token}"}
            )
        )

    def __getstate__(self):
        return {
            "_url": self._url,
            "_get_token_func": self._get_token_func
        }
## TO-DO change this to use the new MCP Server https://github.com/google/mcp/blob/main/examples/launchmybakery/adk_agent/mcp_bakery_app/tools.py
## --> Just need to change the URL to  BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" and add the header "x-goog-user-project": project_id 
    def __setstate__(self, state):
        self.__dict__.update(state)
        token = self._get_token_func()
        super().__init__(
            connection_params=StreamableHTTPConnectionParams(
                url=self._url,
                headers={"Authorization": f"Bearer {token}"}
            )
        )

mcp_toolset = PicklableMcpToolset(
    url=f"{url_mcp_toolset}/mcp/bus-stop-images-toolset",
    get_token_func=get_id_token
)

