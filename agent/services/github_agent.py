from strands import Agent
from agent.model import model, get_groq_model, get_model , ollama_model
from agent.mcp.github_mcp import github_mcp_client
from agent.memory import memory_manager, get_session_manager
from agent.guardrils import GITHUB_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import github_agent_skills
from agent.state import GitHubAgentOutput


github_agent = Agent(
    model=ollama_model,
    name="github-agent",
    tools=[github_mcp_client],
    plugins=[github_agent_skills],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("github-agent-session"),
    system_prompt=GITHUB_AGENT_PROMPT,
)
