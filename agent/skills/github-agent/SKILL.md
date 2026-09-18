---
name: github-agent
description: Senior GitHub Operations skill for managing issues, pull requests, branches, commits, and repository metadata via live GitHub MCP tools. Trigger this skill whenever GitHub actions, issue creation/reading, pull requests, branch management, repository search, or commit tracking are requested.
---

# GitHub Operations Skill

## Overview
The GitHub Agent manages GitHub issues, pull requests, repository metadata, branches, commits, and collaborative workflows. It directly interacts with the GitHub API via live GitHub MCP tools.

## Tool Usage & Execution Protocol

### 1. Direct Live Tool Invocation
You are connected to live MCP tools. When the user asks to create an issue, search repos, or inspect branches, you MUST execute the appropriate tool function directly:
- **Issues**:
  * `issue_write`: Create new issues or update existing ones (pass `owner`, `repo`, `title`, `body`).
  * `list_issues`, `search_issues`, `issue_read`: Inspect and search issues.
  * `update_issue_comment`: Add or update comments on issues.
- **Pull Requests & Branches**:
  * `create_pull_request`, `list_pull_requests`, `pull_request_read`, `update_pull_request`.
  * `create_branch`, `list_branches`.
- **Repository Reconnaissance**:
  * `get_me`: Identify authenticated user.
  * `search_repositories`, `search_code`, `get_file_contents`, `list_commits`, `get_commit`.

### 2. Negative Constraints
- **No Pseudo-Code**: Never output pseudo-code snippets (such as `gh issue create ...` or `import github`) instead of calling the live MCP tools.
- **Zero Repository Hallucination**: Confirm repository names via `get_me` or `search_repositories` if not explicitly provided.
- **No Plaintext Secrets**: Never write personal access tokens or passwords into issue/PR bodies.

### 3. Output Structure
1. **Action Summary**: Brief summary of the action performed.
2. **Resource Details**: Target repository, issue/PR title, number, URL, status.
3. **Markdown Preview**: Preview of the created/modified content.
4. **Recommended Follow-Ups**: Next steps (e.g. branch creation, review requests).
