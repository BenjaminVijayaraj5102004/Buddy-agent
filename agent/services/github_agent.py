from strands import Agent
from agent.model import get_model
from agent.mcp.github_mcp import github_mcp_client
from agent.memory import get_session_manager, SafeSlidingWindowConversationManager
from agent.guardrils import GITHUB_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import github_agent_skills


github_agent = Agent(
    model=get_model(),
    name="github-agent",
    tools=[github_mcp_client],
    plugins=[github_agent_skills],
    hooks=[HumanInTheLoopHook()],
    session_manager=get_session_manager(),
    conversation_manager=SafeSlidingWindowConversationManager(window_size=20),
    system_prompt=GITHUB_AGENT_PROMPT,
)
