from strands import Agent
from strands.tools import tool
from agent.services.api_agent.REST import rest_agent
from agent.model import  get_model
from agent.memory import get_session_manager, SafeSlidingWindowConversationManager
from agent.guardrils import API_MANAGER_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import api_manager_skills


@tool(
    name="REST_Agent",
    description="Delegates REST API endpoint creation, route definitions, and request/response schema design tasks to the specialized REST API agent.",
)
def call_rest_agent(task_description: str) -> str:
    """Invokes the REST API agent to create API endpoints and schemas without database logic."""
    import os
    cwd = os.path.abspath(os.getcwd())
    full_task = f"{task_description}\n[Workspace Directory: {cwd}]"
    try:
        response = rest_agent(full_task)
        return str(response)
    except Exception as e:
        return f"Error executing REST_Agent: {e}"



API_MANAGER = Agent(
    name="API_MANAGER",
    model=get_model(),
    tools=[call_rest_agent],
    plugins=[api_manager_skills],
    hooks=[HumanInTheLoopHook()],
    session_manager=get_session_manager(),
    conversation_manager=SafeSlidingWindowConversationManager(window_size=20),
    system_prompt=API_MANAGER_PROMPT,
)


