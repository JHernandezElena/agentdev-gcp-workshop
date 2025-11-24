from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
import google.genai.types as types
import json

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
PROJECT_ID=os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")

def view_shopping_list(tool_context: ToolContext) -> str:
    """Displays the items currently on the shopping list."""
    print("Executing tool: view_shopping_list")

    # Read from the state using the context object.
    # Provide a default value `[]` in case the list hasn't been created yet.
    current_list = tool_context.state.get("shopping_list", [])

    if not current_list:
        return "The shopping list is currently empty."

    # Format the list for display to the user.
    return "Here is your shopping list:\n- " + "\n- ".join(current_list)

def add_to_shopping_list(item: str, tool_context: ToolContext) -> str:
    """Adds a single item to the shopping list."""
    print(f"Executing tool: add_to_shopping_list with item '{item}'")

    # Read the current list from state
    current_list = tool_context.state.get("shopping_list", [])

    # Modify the list in memory
    if item.lower() not in [i.lower() for i in current_list]:
        current_list.append(item)

    # Write the entire updated list back to the state
    tool_context.state["shopping_list"] = current_list

    return f"'{item}' has been added to the list."


# This function will run after the agent generates its final response. 
# It inspects the user's last message and, if it matches our trigger phrase, it retrieves the list from the state and saves it as a text file artifact.
async def save_list_as_artifact(callback_context: CallbackContext):
    """After the agent runs, check if the user asked to save the list."""
    user_last_message = callback_context.user_content.parts[0].text

    if "save the list" in user_last_message.lower():
        print("Callback triggered: save_list_as_artifact")
        shopping_list = callback_context.state.get("shopping_list", [])

        if not shopping_list:
            print("List is empty, not saving artifact.")
            return

        # Prepare the artifact content
        file_content = "My Shopping List:\n\n- " + "\n- ".join(shopping_list)
        artifact_part = types.Part(text=file_content)

        # Use the context to save the artifact
        try:
            version = await callback_context.save_artifact(
                filename="shopping_list.txt",
                artifact=artifact_part
            )
            print(f"✅ Successfully saved shopping_list.txt as version {version}")
        except ValueError as e:
            print(f"🔴 Error saving artifact: {e}. Is an ArtifactService configured in your runner?")


# Agent Definition
root_agent: Agent = LlmAgent(
    model=GEMINI_MODEL,
    name="ShoppingListAgent",
    instruction="""You are a shopping list assistant.
    - Use the 'add_to_shopping_list' tool to add items.
    - Use the 'view_shopping_list' tool to see the current list.
    - Acknowledge when an item has been added.
    - When the user asks to "save the list", respond with "OK, saving your list."
    """,
    tools=[
        FunctionTool(func=view_shopping_list),
        FunctionTool(func=add_to_shopping_list),
    ],
    after_agent_callback=save_list_as_artifact,
)