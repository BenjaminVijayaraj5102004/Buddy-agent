from strands import Agent
from strands.tools import tool
from agent.services.api_agent.REST import rest_agent as rest_api_agent
from agent.model import model
from agent.memory import memory_manager, get_session_manager
from agent.guardrils import API_MANAGER_PROMPT
from agent.hooks import HumanInTheLoopHook


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
    model=model,
    tools=[call_rest_agent],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("api-manager-session"),
    system_prompt=API_MANAGER_PROMPT,
)

