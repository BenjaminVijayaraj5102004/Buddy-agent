from strands import Agent
from agent.model import  get_model
from agent.mcp.github_mcp import github_rest_mcp_client
from agent.mcp.text_editor_mcp import rest_text_editor_mcp_client
from agent.memory import get_session_manager, SafeSlidingWindowConversationManager
from agent.guardrils import REST_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import rest_agent_skills


rest_agent = Agent(
    model=get_model(),
    name="REST_API",
    tools=[github_rest_mcp_client, rest_text_editor_mcp_client],
    plugins=[rest_agent_skills],
    hooks=[HumanInTheLoopHook()],
    session_manager=get_session_manager(),
    conversation_manager=SafeSlidingWindowConversationManager(window_size=20),
    system_prompt=REST_AGENT_PROMPT,
)


