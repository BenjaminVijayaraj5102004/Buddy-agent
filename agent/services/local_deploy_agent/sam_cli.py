from strands import Agent
from agent.memory import memory_manager, get_session_manager
from agent.model import model
from agent.mcp.samcli_mcp import samcli_mcp_client
from agent.mcp.text_editor_mcp import sam_text_editor_mcp_client
from agent.guardrils import SAM_CLI_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook


sam_cli_agent = Agent(
    model=model,
    name="sam-cli-agent",
    tools=[samcli_mcp_client, sam_text_editor_mcp_client],
    hooks=[HumanInTheLoopHook()],
    memory_manager=memory_manager,
    session_manager=get_session_manager("sam-cli-agent-session"),
    system_prompt=SAM_CLI_AGENT_PROMPT,
)




