import os
from mcp.client.stdio import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient
from agent.config import settings


# Build stdio parameters for text-editor MCP server
text_editor_server_params = StdioServerParameters(
    command=settings.TEXT_EDITOR_MCP_COMMAND,
    args=settings.TEXT_EDITOR_MCP_ARGS,
    env=dict(os.environ),
)


def get_stdio_transport():
    """Returns standard I/O client transport for text editor MCP server."""
    return stdio_client(text_editor_server_params)


# Initialize MCPClient for Text Editor
text_editor_mcp_client = MCPClient(
    get_stdio_transport,
    startup_timeout=60,
)

if __name__ == "__main__":
    with text_editor_mcp_client:
        tools = text_editor_mcp_client.list_tools_sync()
        print(f"Total available Text Editor tools: {len(tools)}\n")
        for item in tools:
            print(f"- {item.tool_name}: {item.mcp_tool.description}")
