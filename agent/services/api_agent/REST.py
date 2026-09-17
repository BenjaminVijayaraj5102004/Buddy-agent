from strands import Agent
from agent.model import model
from agent.mcp.github_mcp import github_mcp_client
from agent.memory import memory_manager, get_session_manager



REST_SYSTEM_PROMPT = """You are a REST API Design and Development Agent.

Your mission is to design and write clean, robust RESTful API endpoints and data schemas.

Core Guidelines:
1. Endpoints & Schemas Only:
   - Focus strictly on API routing (e.g., FastAPI / Flask), HTTP methods, status codes, and request/response validation schemas (e.g., Pydantic).
   - DO NOT write database connection code, ORM models, or persistence logic.
   - For handlers, use mock data, dummy return dictionaries, or service stubs.

2. Tools & Context:
   - When designing an endpoint, use GitHub MCP tools (search_code, search_repositorey ,get_file_contents) to scan the codebase for existing endpoints and patterns.
   - Reuse existing design patterns (e.g., folder structure, decorator usage, error handling) when found in the codebase.
   - Search memory to leverage common API design conventions.

3. API Standards:
   - Use standard REST conventions (plural nouns for resources).
   - Return appropriate HTTP status codes (e.g., 201, 200, 204, 400, 422).
   - Use Pydantic BaseModel for request payloads and response models with proper type hints and field descriptions.
"""



rest_agent = Agent(
    model=model,
    name="REST_API",
    tools=[github_mcp_client],
    memory_manager=memory_manager,
    session_manager=get_session_manager("rest-agent-session"),
    system_prompt=REST_SYSTEM_PROMPT,
)

if __name__ == "__main__":
    result = rest_agent("List out the tools you are using to write code")
    print(f"\nTools used: {list(result.metrics.tool_metrics.keys())}\n")
    print(result)