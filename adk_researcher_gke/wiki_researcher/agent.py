"""
Defines the core multi-agent workflow. Configures individual agents (Researcher, 
Screenwriter, File Writer), assigns their specific tools, and orchestrates 
their collaboration using the ADK's SequentialAgent pattern.
"""
import os
import logging
import google.cloud.logging

from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool  # import
from google.genai import types
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# public_url = os.getenv("AGENT_PUBLIC_URL", "http://localhost:8080")
public_url = 'http://136.112.90.99'

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)

# Tools


def append_to_state(
    tool_context: ToolContext, field: str, response: str
) -> dict[str, str]:
    """Append new output to an existing state key.

    Args:
        field (str): a field name to append to
        response (str): a string to append to the field

    Returns:
        dict[str, str]: {"status": "success"}
    """
    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    logging.info(f"[Added to {field}] {response}")
    return {"status": "success"}



# Agents

root_agent = Agent(
    name="wiki_researcher",
    model=model_name,
    description="Answer research questions using Wikipedia.",
    instruction="""
    PROMPT:
    { PROMPT? }

    PLOT_OUTLINE:
    { PLOT_OUTLINE? }

    CRITICAL_FEEDBACK:
    { CRITICAL_FEEDBACK? }

    INSTRUCTIONS:
    - If there is a CRITICAL_FEEDBACK, use your wikipedia tool to do research to solve those suggestions
    - If there is a PLOT_OUTLINE, use your wikipedia tool to do research to add more historical detail
    - If these are empty, use your Wikipedia tool to gather facts about the person in the PROMPT
    - Use the 'append_to_state' tool to add your research to the field 'research'.
    - Summarize what you have learned.
    Now, use your Wikipedia tool to do research.
    """,
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
    ),
    tools=[
        LangchainTool(tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())),
        append_to_state,
    ],
)

researcher_agent_card = AgentCard(
    name=root_agent.name,
    url=public_url, 
    description="Answer research questions using Wikipedia.",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"]
)

# a2a_app = to_a2a(root_agent, port=8080)
a2a_app = to_a2a(root_agent, agent_card=researcher_agent_card)

# Only create the A2A app if this file is run directly via 'python agent.py'
# if __name__ == "__main__":
#     import uvicorn
#     # This exposes your agent via the A2A protocol
#     a2a_app = to_a2a(root_agent, port=8001)
#     uvicorn.run(a2a_app, host="0.0.0.0", port=8001)