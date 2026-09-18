from strands import Agent
from agent.memory import memory_manager, get_session_manager
from agent.model import model, get_groq_model, get_model , ollama_model
from agent.mcp.samcli_mcp import samcli_mcp_client
from agent.mcp.text_editor_mcp import sam_text_editor_mcp_client
from agent.guardrils import SAM_CLI_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import sam_cli_agent_skills
from agent.state import SAMCLIAgentOutput


sam_cli_agent = Agent(
    model=ollama_model,
    name="sam-cli-agent",
    tools=[samcli_mcp_client, sam_text_editor_mcp_client],
    plugins=[sam_cli_agent_skills],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("sam-cli-agent-session"),
    system_prompt=SAM_CLI_AGENT_PROMPT,
)




