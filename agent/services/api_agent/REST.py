from strands import Agent
from agent.model import model, get_groq_model, get_model , ollama_model
from agent.mcp.github_mcp import github_rest_mcp_client
from agent.mcp.text_editor_mcp import rest_text_editor_mcp_client
from agent.memory import memory_manager, get_session_manager
from agent.guardrils import REST_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import rest_agent_skills
from agent.state import RESTAgentOutput

rest_agent = Agent(
    model=ollama_model,
    name="REST_API",
    tools=[github_rest_mcp_client, rest_text_editor_mcp_client],
    plugins=[rest_agent_skills],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("rest-agent-session"),
    system_prompt=REST_AGENT_PROMPT,
)


