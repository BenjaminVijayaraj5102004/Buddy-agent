from strands import Agent
from agent.model import model
from agent.mcp.github_mcp import github_rest_mcp_client
from agent.mcp.text_editor_mcp import rest_text_editor_mcp_client
from agent.memory import memory_manager, get_session_manager
from agent.guardrils import REST_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook

rest_agent = Agent(
    model=model,
    name="REST_API",
    tools=[github_rest_mcp_client, rest_text_editor_mcp_client],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("rest-agent-session"),
    system_prompt=REST_AGENT_PROMPT,
)


