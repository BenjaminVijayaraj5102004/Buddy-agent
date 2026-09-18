from strands import Agent
from strands.tools import tool
from agent.services.api_agent.REST import rest_agent as rest_api_agent
from agent.model import model, get_groq_model, get_model , ollama_model
from agent.memory import memory_manager, get_session_manager
from agent.guardrils import API_MANAGER_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import api_manager_skills
from agent.state import APIManagerOutput


@tool(
    name="REST_Agent",
    description="Delegates REST API endpoint creation, route definitions, and request/response schema design tasks to the specialized REST API agent.",
)
def call_rest_agent(task_description: str) -> str:
    """Invokes the REST API agent to create API endpoints and schemas without database logic."""
    response = rest_api_agent(task_description)
    return str(response)


API_MANAGER = Agent(
    name="API_MANAGER",
    model=ollama_model,
    tools=[call_rest_agent],
    plugins=[api_manager_skills],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("api-manager-session"),
    system_prompt=API_MANAGER_PROMPT,
)

