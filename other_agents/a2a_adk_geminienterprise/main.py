import os

from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv

from agent_executor import ReimbursementAgentExecutor
from gemini_agent import GeminiAgent

load_dotenv()

# The URL of your deployed agent.
# It's best to set this as an environment variable in your deployment.
AGENT_URL = os.environ.get("AGENT_URL", "http://127.0.0.1:8000")

# 1. Create the Agent, AgentCard, RequestHandler, and App at the global scope.
#    This is more efficient as it's done only once when the app instance starts.
agent = GeminiAgent()
agent_card = agent.create_agent_card(AGENT_URL)

request_handler = DefaultRequestHandler(
    agent_executor=ReimbursementAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

# 2. The application server will automatically look for this 'app' variable.
app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
).build()
