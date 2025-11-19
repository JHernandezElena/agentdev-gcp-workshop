from typing import Optional

from google import genai
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.apps import App
from google.adk.plugins.save_files_as_artifacts_plugin import \
    SaveFilesAsArtifactsPlugin
from google.adk.tools import google_search
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from google.genai.types import HttpOptions

CHANGED_LIVERY_IMAGE_ARTIFACT_NAME = "changed_livery.png"


async def after_livery_swapper_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    artifact = await callback_context.load_artifact(filename=CHANGED_LIVERY_IMAGE_ARTIFACT_NAME)
    return types.Content(
        parts=[artifact],
        role="model",
    )


async def swap_airline_livery(tool_context: ToolContext, target_airline: str):
    """Takes the first image from the uploaded artifacts and invokes Nano Banana to replace
    the livery of the aircraft with that of the given airline.
    """
    available_files = await tool_context.list_artifacts()

    if not len(available_files):
        return "There are no images uploaded"

    artifact_part = await tool_context.load_artifact(available_files[0])

    client = genai.Client(http_options=HttpOptions(api_version="v1"))

    content_parts = [artifact_part, types.Part.from_text(
        text=f"You are a helpful image editor artist. Replace the livery of the given aircraft in the picture with the livery of {target_airline}")
    ]
    contents = [
        types.Content(
            role="user",
            parts=content_parts,
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
    )
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=contents,
        config=generate_content_config,
    )

    for cd in response.candidates:
        for p in cd.content.parts:
            if p.inline_data is None:
                # Skip this part, as it does not have inline data (and thus it's not an image)
                continue

            if p.inline_data.mime_type == "image/png":
                # Save the artifact with the hardcoded name.
                await tool_context.save_artifact(
                    filename=CHANGED_LIVERY_IMAGE_ARTIFACT_NAME,
                    artifact=p,
                )
                return f"Success. Image saved as artifact: {CHANGED_LIVERY_IMAGE_ARTIFACT_NAME}"

    return "No image was generated"


airline_identifier_agent = Agent(
    model='gemini-2.5-flash',
    name='airline_identifier_agent',
    description='An agent that identifies airlines in aircraft photos.',
    instruction='You are a specialist in aircraft identification. Given an image artifact, analyze the image and return ONLY the name of the airline.',
    output_key="airline_name",
)


airline_hub_researcher_agent = Agent(
    model='gemini-2.5-flash',
    name='AirlineHubReseracherAgent',
    description='An agent that looks for an airline\'s hub in Google.',
    instruction=(
        """Your goal is to take an airline name as an input and look up in Google the location of its main hub.

You MUST return ONLY the name of the hub city. Example: "Dallas", "Madrid"."""
    ),
    output_key="airline_hub",
    tools=[google_search],
)

airline_competitor_researcher_agent = Agent(
    model='gemini-2.5-flash',
    name='AirlineCompetitorReseracherAgent',
    description='An agent that looks for an airline\'s main competitor in Google.',
    instruction=(
        """Your goal is to take an airline name as an input and look up in Google the name of its biggest competitor in the domestic market.

You MUST return ONLY the name of the aircraft. Example: "American Airlines", "Iberia"."""
    ),
    output_key="airline_competitor",
    tools=[google_search],
)

airline_researcher_agent = ParallelAgent(
    name='AirlineResearcherAgent',
    description='An agent that runs different searches in parallel related to an airline.',
    sub_agents=[
        airline_hub_researcher_agent,
        airline_competitor_researcher_agent,
    ],
)

aircraft_livery_swapper_agent = Agent(
    model='gemini-2.5-flash',
    name='AircraftLiverySwapperAgent',
    description='An agent that takes an image of an aircraft and returns a new image with the same aircraft in a different livery.',
    instruction=(
        """You are a helpful image editing agent.

Your goal is to take an artifact image of an aircraft and modify its livery to the livery of this airline: {airline_competitor}.

Use the `swap_airline_livery` tool to generate a new image, then return it in your response."""
    ),
    tools=[swap_airline_livery, load_artifacts_tool],
    after_agent_callback=after_livery_swapper_agent_callback,
)

root_agent = SequentialAgent(
    name='root_agent',
    description='Executes the airline identification and research pipeline.',
    sub_agents=[
        airline_identifier_agent,
        airline_researcher_agent,
        aircraft_livery_swapper_agent,
    ],
)

app = App(
    name="multimodal_agent",
    root_agent=root_agent,
    plugins=[SaveFilesAsArtifactsPlugin()],
)
