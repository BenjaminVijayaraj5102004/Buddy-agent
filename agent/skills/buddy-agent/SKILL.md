---
name: buddy-agent
description: Master orchestrator skill for classifying intent, extracting arguments (file paths, specs), and delegating to api_manager, sam_cli_agent, or github_agent.
---

# Buddy Agent Orchestrator Skill

## Intent Routing
- **`call_api_manager`**: REST APIs, FastAPI/Flask routes, HTTP verbs, Pydantic schemas, pagination.
- **`call_sam_cli_agent`**: AWS SAM CLI, `template.yaml`, sam init/build/deploy, Lambda, S3 hosting.
- **`call_github_agent`**: GitHub issues, PRs, branches, repository search, commits.
- **Direct Response**: Greetings, general programming questions, or conversation context lookups.

## Argument Extraction
Always extract and preserve exact user arguments in `task_description`:
- File and folder paths (e.g. `e:\Hackathon\buddy-agent\example\items.py`)
- HTTP methods, routes, framework preferences, AWS parameters, GitHub repo names.
