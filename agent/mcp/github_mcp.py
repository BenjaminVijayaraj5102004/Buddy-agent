import os
from dotenv import load_dotenv
from strands.tools.mcp import MCPClient
from strands import tool

load_dotenv()

def coding_tools() -> list[str]:
    """Returns the allowed GitHub coding tools."""
    return [
        "search_code",
        "search_repositories",
        "get_file_contents",
    ]



# Initialize MCP client with tool filters
github_mcp_client = MCPClient(
    url="https://api.githubcopilot.com/mcp/",
    headers={"Authorization": f"Bearer {os.getenv('GITHUB_PAT')}"},
    tool_filters={
        "allowed": coding_tools(),
    },
)

def my_classifier(event, **kwargs):
    """Classifier that allows only GitHub coding tools (search_code, search_repositories, get_file_contents).
    
    All other tools require human approval.
    """
    from strands.vended_interventions.hitl.classifier import ClassifierResult

    tool_name = event.tool_use["name"]
    allowed = set(coding_tools())

    # Check naming conventions: exact match or prefix-stripped match (e.g. github_search_code)
    is_allowed = (
        tool_name in allowed
        or any(tool_name.endswith(f"_{t}") or tool_name == t for t in allowed)
    )

    requires_approval = not is_allowed
    return ClassifierResult(
        requires_human_in_the_loop=requires_approval,
        reason=f"Tool '{tool_name}' requires human approval" if requires_approval else None,
    )


if __name__ == "__main__":
    with github_mcp_client:
        tools = github_mcp_client.list_tools_sync()
        print(f"Total available tools: {len(tools)}\n")
        for item in tools:
            print(f"- {item.tool_name}: {item.mcp_tool.description}")


@tool(name="addition", description="Add two integers and return the sum")
def addition(a: int, b: int) -> int:
    """This tool is used for adding two numbers."""
    return int(a) + int(b)


@tool(name="multiply", description="Multiply two integers and return the product")
def multiply(a: int, b: int) -> int:
    """This tool is used for multiplying two numbers."""
    return int(a) * int(b)
