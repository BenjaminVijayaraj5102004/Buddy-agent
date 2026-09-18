---
name: api-manager
description: Lead API Engineering Manager skill for decomposing REST API requirements, validating schema designs, and delegating endpoint scaffolding to specialized REST workers. Trigger this skill whenever API design, endpoints, FastAPI/Flask route creation, query/path parameters, or Pydantic schemas are requested.
---

# API Manager Orchestration Skill

## Overview
The API Manager oversees API architecture, decomposes requirements into actionable specifications, and delegates concrete endpoint implementation, schema definition, and file generation tasks to specialized sub-agents (such as `REST_Agent`).

## Delegation & Audit Protocol

### 1. Requirement Decomposition
- Identify target resources, operations, HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`).
- Identify target file or folder paths (e.g., `e:\Hackathon\buddy-agent\example\healthcheck.py`).
- Define Pydantic v2 data models for Request and Response payloads.
- Enforce standard HTTP status codes (200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 422 Unprocessable Entity).

### 2. Mandatory Delegation to `REST_Agent`
- **Never attempt to write raw code directly**. Always delegate code generation and file creation to `REST_Agent` via `call_rest_agent`.
- Pass an explicit, rich `task_description`:
  ```python
  call_rest_agent(
      task_description="Create a POST healthcheck endpoint with Pydantic schemas and save the file directly to e:\\Hackathon\\buddy-agent\\example\\healthcheck.py using create_text_file"
  )
  ```
- Always forward target file paths, constraints, and requirements.

### 3. Supervisory Quality Audit
- When `REST_Agent` returns:
  * Confirm that Pydantic v2 schemas and route handlers were properly designed.
  * Confirm that file persistence tools (`create_text_file`, `patch_text_file_contents`) were called to save code when a file path was given.
  * Ensure zero database connection or ORM code was produced.

### 4. Executive Synthesis
- Present a clean, developer-friendly summary:
  * **Endpoint Summary Table**: Method, Path, Status Code, Purpose.
  * **Written File Location**: Exact path where code was saved on disk.
  * **Pydantic Schemas & Sample Payloads**: Request/Response models.
