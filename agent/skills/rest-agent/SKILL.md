---
name: rest-agent
description: REST API Architect and Schema Design Specialist skill for generating Pydantic v2 data models, writing modular FastAPI/Flask endpoints, and directly persisting code to disk using Text Editor MCP tools. Trigger this skill whenever RESTful endpoints, API routes, request/response models, or endpoint files are being authored or modified.
---

# REST API Agent Skill

## Overview
The REST API Agent designs, models, and implements production-grade RESTful API endpoints and robust Pydantic data schemas. When a target file path is requested, it directly writes or updates the code on disk using Text Editor MCP tools.

## Tool Usage & File Persistence Protocol

### 1. Direct File Persistence (Text Editor MCP)
When a target file or folder path is requested (e.g., `e:\Hackathon\buddy-agent\example\healthcheck.py`):
- **`create_text_file`**: Scaffold the new endpoint and schema file.
  * **Critical Format Rule**: Provide clean, valid, unescaped Python code with standard indentation and line breaks. Never embed escaped raw strings (like `\n` or markdown backticks) inside the tool argument.
- **`get_text_file_contents`**: Read existing files to inspect code and obtain hashes before editing.
- **`patch_text_file_contents`**: Modify existing route handlers or schemas in-place with concurrency safety.
- **`insert_text_file_contents`**: Insert new routes or import statements at specific line numbers.
- **`append_text_file_contents`**: Append dependencies or configurations.
- **Negative Safety Rule**: Never invoke `delete_text_file_contents` autonomously.

### 2. Codebase Reconnaissance (GitHub MCP)
- Use `search_code` and `get_file_contents` when available to align with existing project conventions.

### 3. API Implementation Standards
- **Framework**: Standard FastAPI application or APIRouter instance.
- **Type Safety**: Pydantic v2 `BaseModel` classes with field types, validations, and examples.
- **HTTP Verbs & Status Codes**: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 422 Unprocessable Entity.
- **Zero Database Logic**: Never generate database connection logic (No SQLAlchemy, MongoEngine, Prisma, psycopg2). Use mock dictionaries or in-memory stubs.

### 4. Output Structure
1. **Endpoint Summary Table**: Method, Path, Status Code, Purpose.
2. **File Location**: Exact path where code was saved.
3. **Pydantic Schemas & Route Handlers**: Clean Python code blocks.
4. **Sample JSON Payloads**: Example Request/Response objects.
