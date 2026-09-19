---
name: rest-agent
description: REST API Architect skill for authoring Pydantic v2 schemas, FastAPI routes, and saving code to disk via GitHub MCP and Text Editor MCP tools.
---

# REST Agent Skill

## Tool Usage & Implementation
1. **File Creation & Local Editing (Text Editor MCP)**:
   - `create_text_file`: Write complete, unescaped Python code directly to target absolute file path.
   - `get_text_file_contents` / `patch_text_file_contents`: Inspect or update existing local files on disk.
2. **GitHub MCP Tools (Remote Reconnaissance & Code Search)**:
   - `search_code`: Search GitHub for existing patterns, schema structures, and routes.
   - `get_file_contents`: Read remote GitHub repo files (requires `owner` and `repo`). *Never pass local disk paths.*
   - `search_repositories`: Find relevant template or reference repositories.
3. **Code Standards**:
   - Complete Pydantic v2 `BaseModel` classes with explicit type annotations.
   - Clean FastAPI `APIRouter` route handlers.
   - Strictly zero database/ORM logic (use mock dictionaries or in-memory stubs).
