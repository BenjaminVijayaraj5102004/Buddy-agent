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


def rest_text_editor_tools() -> list[str]:
    """Returns permitted Text Editor tools for REST API Agent.

    - create_text_file: Scaffolding new endpoints, routes, models, or test files from scratch.
    - get_text_file_contents: Reading route handlers or schemas to check existing code and obtain hashes.
    - insert_text_file_contents: Appending new routes, importing modules, or adding schemas without patch offsets.
    - append_text_file_contents: Appending new dependency requirements or adding lines to config files.
    - patch_text_file_contents: Modifying existing route handler logic in-place with concurrency safety.
    """
    return [
        "create_text_file",
        "get_text_file_contents",
        "insert_text_file_contents",
        "append_text_file_contents",
        "patch_text_file_contents",
    ]


def sam_text_editor_tools() -> list[str]:
    """Returns permitted Text Editor tools for SAM CLI Agent.

    - get_text_file_contents: Inspecting template.yaml / samconfig.toml and fetching validation hashes.
    - patch_text_file_contents: Updating environment variables, memory limits, or handler paths in YAML blocks.
    - insert_text_file_contents: Inserting new Serverless function definitions or event mappings.
    - create_text_file: Creating initial template.yaml, samconfig.toml, or deployment scripts.
    """
    return [
        "get_text_file_contents",
        "patch_text_file_contents",
        "insert_text_file_contents",
        "create_text_file",
    ]


# Restricted Text Editor MCP client for REST API Agent
rest_text_editor_mcp_client = MCPClient(
    get_stdio_transport,
    tool_filters={
        "allowed": rest_text_editor_tools(),
    },
    startup_timeout=60,
)

# Restricted Text Editor MCP client for SAM CLI Agent
sam_text_editor_mcp_client = MCPClient(
    get_stdio_transport,
    tool_filters={
        "allowed": sam_text_editor_tools(),
    },
    startup_timeout=60,
)

# Full Text Editor client with complete toolset
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
