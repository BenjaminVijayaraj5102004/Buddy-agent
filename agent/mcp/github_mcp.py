from agent.config.settings import settings
from strands.tools.mcp import MCPClient


def rest_coding_tools() -> list[str]:
    """Returns the restricted GitHub tools for REST API reconnaissance."""
    return [
        "search_code",
        "search_repositories",
        "get_file_contents",
    ]


# Restricted GitHub client for REST Agent
github_rest_mcp_client = MCPClient(
    url="https://api.githubcopilot.com/mcp/",
    headers={"Authorization": f"Bearer {settings.GITHUB_PAT}"},
    tool_filters={
        "allowed": rest_coding_tools(),
    },
)

# Full GitHub client with complete toolset (issues, PRs, branches, etc.) for GitHub Agent
github_mcp_client = MCPClient(
    url="https://api.githubcopilot.com/mcp/",
    headers={"Authorization": f"Bearer {settings.GITHUB_PAT}"},
)


if __name__ == "__main__":
    with github_mcp_client:
        tools = github_mcp_client.list_tools_sync()
        print(f"Total available GitHub tools: {len(tools)}\n")
        for item in tools:
            print(f"- {item.tool_name}: {item.mcp_tool.description}")
