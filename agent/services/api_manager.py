from strands import Agent
from strands.tools import tool
from agent.services.api_agent.REST import rest_agent as rest_api_agent
from agent.model import model
from agent.memory import memory_manager, get_session_manager


@tool(
    name="REST_Agent",
    description="Delegates REST API endpoint creation, route definitions, and request/response schema design tasks to the specialized REST API agent.",
)
def call_rest_agent(task_description: str) -> str:
    """Invokes the REST API agent to create API endpoints and schemas without database logic."""
    response = rest_api_agent(task_description)
    return str(response)


API_MANAGER_PROMPT = """You are the API Manager Agent responsible for routing, coordinating, and orchestrating API tasks.

Key Guidelines:
1. Delegation:
   - For all REST API design tasks, route definitions, HTTP status codes, and Pydantic request/response schemas, ALWAYS delegate the task to the `REST_Agent` tool.
   - Do NOT attempt to write REST endpoints or schemas yourself when the `REST_Agent` tool is available.

2. Quality Check:
   - Ensure the delegated agent's output adheres to standards: endpoints and schemas only, with zero database connection or storage code.
   - Present the final output clearly with endpoint descriptions, HTTP methods, and Pydantic schemas.
"""

API_MANAGER = Agent(
    name="API_MANAGER",
    model=model,
    tools=[call_rest_agent],
    memory_manager=memory_manager,
    session_manager=get_session_manager("api-manager-session"),
    system_prompt=API_MANAGER_PROMPT,
)

if __name__ == "__main__":
    result = API_MANAGER("Write a post endpoint for new user signup")
    print(f"\nTools used: {list(result.metrics.tool_metrics.keys())}\n")
    print(result)