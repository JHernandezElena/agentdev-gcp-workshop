#https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/agent-engine/tutorial_langgraph.ipynb

from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, MessageGraph
from langgraph.prebuilt import ToolNode

import vertexai 
from vertexai import agent_engines

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
PROJECT_ID=os.getenv("PROJECT_ID")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET) 

def get_product_details(product_name: str):
    """Gathers basic details about a product."""
    details = {
        "smartphone": "A cutting-edge smartphone with advanced camera features and lightning-fast processing.",
        "coffee": "A rich, aromatic blend of ethically sourced coffee beans.",
        "shoes": "High-performance running shoes designed for comfort, support, and speed.",
        "headphones": "Wireless headphones with advanced noise cancellation technology for immersive audio.",
        "speaker": "A voice-controlled smart speaker that plays music, sets alarms, and controls smart home devices.",
    }
    return details.get(product_name, "Product details not found.")



def router(state: list[BaseMessage]) -> Literal["get_product_details", "__end__"]:
    """Initiates product details retrieval if the user asks for a product."""
    # Get the tool_calls from the last message in the conversation history.
    tool_calls = state[-1].tool_calls
    # If there are any tool_calls
    if len(tool_calls):
        # Return the name of the tool to be called
        return "get_product_details"
    else:
        # End the conversation flow.
        return "__end__"


class SimpleLangGraphApp:
    def __init__(self, project: str, location: str) -> None:
        self.project_id = project
        self.location = location

    # The set_up method is used to define application initialization logic
    def set_up(self) -> None:
        # The additional code required for OTEL
        from opentelemetry import trace
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from openinference.instrumentation.langchain import LangChainInstrumentor
        import google.cloud.trace_v2 as cloud_trace_v2
        import google.auth

        credentials, _ = google.auth.default()

        trace.set_tracer_provider(TracerProvider())
        cloud_trace_exporter = CloudTraceSpanExporter(
            project_id=self.project_id,
            client=cloud_trace_v2.TraceServiceClient(
                credentials=credentials.with_quota_project(self.project_id),
            ),
        )
        trace.get_tracer_provider().add_span_processor(
            SimpleSpanProcessor(cloud_trace_exporter)
        )
        LangChainInstrumentor().instrument()
        # end of additional code required
        
        model = ChatVertexAI(model=GEMINI_MODEL)

        builder = MessageGraph()

        model_with_tools = model.bind_tools([get_product_details])
        builder.add_node("tools", model_with_tools)

        tool_node = ToolNode([get_product_details])
        builder.add_node("get_product_details", tool_node)
        builder.add_edge("get_product_details", END)

        builder.set_entry_point("tools")
        builder.add_conditional_edges("tools", router)

        self.runnable = builder.compile()

    # The query method will be used to send inputs to the agent
    def query(self, message: str):
        """Query the application.

        Args:
            message: The user message.

        Returns:
            str: The LLM response.
        """
        chat_history = self.runnable.invoke(HumanMessage(message))

        return chat_history[-1].content
