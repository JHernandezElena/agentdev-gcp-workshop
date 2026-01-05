
import os
from google.adk.agents import LlmAgent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from google.adk.tools import FunctionTool
import json

# --- DEFINE YOUR TOOLS HERE ---
def get_weekly_planner(date: str) -> str:
    """Gets the list of activities for a given day."""
    # In a real scenario, you might call an  API here.
    if date:
        match date[:2]:
            case "Mo":
                activities = ["Team meeting at 10 AM", "Code review at 2 PM", "Plan sprint tasks"]
            case "Tu":
                activities = ["Client demo at 11 AM", "Develop new feature", "Documentation update"]
            case "We":
                activities = ["Mid-week sync-up", "Bug fixing session", "Research new technologies"]
            case "Th":
                activities = ["Code refactoring", "Prepare for Friday's demo", "Mentoring session"]
            case "Fr":
                activities = ["Product demo", "Retrospective meeting", "Knowledge sharing session"]
            case _:
                activities = ["No specific activities planned for this day."]
        return f"The activities for '{date}' are: {', '.join(activities)}"
    else:
        return f"The activities are: Go for a walk, Read a book, Practice yoga."

def get_weather(location: str) -> str:
    """
    Retrieves weather forecast data for a given location and time period.

    Args:
        location (str): The location for which to retrieve weather data.        
    Returns:
        str: A string containing the weather forecast data.
    """
    # This is a placeholder. In a real application, you would call an external weather API.
    # For demonstration purposes, we'll return a mock JSON response.
    mock_data = {
        "location": location,
        "period": "today",
        "forecast": "sunny",
        "temperature": "25°C",
        "humidity": "60%",
        "wind_speed": "10 km/h"
    }
    return json.dumps(mock_data)

#-- AGENT DEFINITION ---

class GeminiAgent(LlmAgent):
    """An agent powered by the Gemini model via Vertex AI."""

    # --- AGENT IDENTITY ---
    # These are the default values. The notebook can override them.
    name: str = "gemini_agent"
    description: str = "A helpful assistant powered by Gemini."

    def __init__(self, **kwargs):
        print("Initializing GeminiAgent...")
        # --- SET YOUR SYSTEM INSTRUCTIONS HERE ---
        instructions = """
        You are a helpful and friendly assistant. Your task is to answer user queries using puns, if a city is mentioned, answer in the language spoken there. 
        You can use the weather tool to find the weather in a location.
        You can use the weekly planner tool to get a list of activities for a given day of the week Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.
        """
        
        # --- MY TOOLS HERE ---
        tools = [
            get_weekly_planner,
            get_weather
        ]

        super().__init__(
            model=os.environ.get("MODEL", "gemini-2.5-flash"),
            instruction=instructions,
            tools=tools,
            **kwargs,
        )


    def create_agent_card(self, agent_url: str) -> "AgentCard":
        return AgentCard(
            
name=self.name,
            description=self.description,
            url=agent_url,
            version="1.0.0",
            defaultInputModes=["text/plain"],
            defaultOutputModes=["text/plain"],
            capabilities=AgentCapabilities(streaming=True),
            skills=[
                AgentSkill(
                    id="chat",
                    name="Chat Skill",
                    description="Chat with the My friendly Gemini agent.",
                    tags=["chat"],
                    examples=["What's the weather like in Paris today?","What are my activities for Monday?"]
                )
            ]

        )
