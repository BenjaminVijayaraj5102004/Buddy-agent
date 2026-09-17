from agent.config.settings import settings
from strands.tools.mcp import MCPClient
from strands import tool



github_mcp_client = MCPClient(
    url="https://api.githubcopilot.com/mcp/",
    headers={"Authorization": f"Bearer {settings.GITHUB_PAT}"},
)


if __name__ == "__main__":
    with github_mcp_client:
        tools = github_mcp_client.list_tools_sync()
        print(f"Total available tools: {len(tools)}\n")
        for item in tools:
            print(f"- {item.tool_name}: {item.mcp_tool.description}")