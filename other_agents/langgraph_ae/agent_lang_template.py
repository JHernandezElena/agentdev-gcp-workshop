#https://docs.cloud.google.com/agent-builder/agent-engine/develop/langgraph

from vertexai import agent_engines
from vertexai.generative_models import grounding, Tool

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
PROJECT_ID=os.getenv("PROJECT_ID")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
):
    """Retrieves the exchange rate between two currencies on a specified date.

    Uses the Frankfurter API (https://api.frankfurter.app/) to obtain
    exchange rate data.

    Args:
        currency_from: The base currency (3-letter currency code).
            Defaults to "USD" (US Dollar).
        currency_to: The target currency (3-letter currency code).
            Defaults to "EUR" (Euro).
        currency_date: The date for which to retrieve the exchange rate.
            Defaults to "latest" for the most recent exchange rate data.
            Can be specified in YYYY-MM-DD format for historical rates.

    Returns:
        dict: A dictionary containing the exchange rate information.
            Example: {"amount": 1.0, "base": "USD", "date": "2023-11-24",
                "rates": {"EUR": 0.95534}}
    """
    import requests
    response = requests.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
    )
    return response.json()

agent = agent_engines.LanggraphAgent(
    model=GEMINI_MODEL,
    tools=[get_exchange_rate],
    enable_tracing=True,
)
response = agent.query(input={"messages": [
    ("user", "When is the next total solar eclipse in US?"),
]})
print(response)