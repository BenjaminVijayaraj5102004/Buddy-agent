---
name: github-agent
description: GitHub Operations skill for managing issues, PRs, branches, commits, and repository metadata via live GitHub MCP tools.
---

# GitHub Agent Skill

## Tool Usage
1. **Direct Tool Invocation**:
   - Issues: `issue_write`, `list_issues`, `search_issues`, `update_issue_comment`.
   - PRs & Branches: `create_pull_request`, `list_pull_requests`, `create_branch`, `list_branches`.
   - Repo: `get_me`, `search_repositories`, `search_code`, `get_file_contents`, `list_commits`.
2. **Rules**: Always execute live MCP tools directly (no pseudo-code). Never write plaintext tokens or secrets.
