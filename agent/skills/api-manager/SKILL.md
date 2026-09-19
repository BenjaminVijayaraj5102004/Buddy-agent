---
name: api-manager
description: API Engineering Manager skill for decomposing REST API requirements and delegating endpoint/schema creation to REST_Agent.
---

# API Manager Skill

## Protocol
1. **Requirement Analysis**: Decompose routes, verbs (`GET`, `POST`, `PUT`, `DELETE`), Pydantic v2 schemas, and target file paths.
2. **Delegation to `REST_Agent`**: Always call `call_rest_agent(task_description=...)` with complete specifications and file destinations.
3. **Audit & Summary**: Ensure zero database/ORM logic is present and return a clean, concise API specification.
