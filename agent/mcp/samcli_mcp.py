import os
from mcp.client.stdio import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient
from agent.config import settings


# Build stdio parameters based on uvx awslabs.aws-serverless-mcp-server and mock credentials
samcli_server_params = StdioServerParameters(
    command=settings.AWS_SERVERLESS_MCP_COMMAND,
    args=settings.AWS_SERVERLESS_MCP_ARGS,
    env={
        **os.environ,
        "AWS_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY,
        "AWS_SESSION_TOKEN": settings.AWS_SESSION_TOKEN,
        "AWS_REGION": settings.AWS_REGION,
    },
)


def get_stdio_transport():
    """Returns standard I/O client transport without using lambda functions."""
    return stdio_client(samcli_server_params)


# Initialize MCPClient for AWS Serverless
samcli_mcp_client = MCPClient(
    get_stdio_transport,
    startup_timeout=60,
)

if __name__ == "__main__":
    with samcli_mcp_client:
        tools = samcli_mcp_client.list_tools_sync()
        print(f"Total available AWS Serverless tools: {len(tools)}\n")
        for item in tools:
            print(f"- {item.tool_name}: {item.mcp_tool.description}")