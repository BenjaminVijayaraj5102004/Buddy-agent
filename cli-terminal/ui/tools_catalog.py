"""
MCP Tools Catalog & HITL Governance Filter Engine for Buddy Agent
Provides GitHub MCP, SAM CLI MCP, and Text Editor MCP tools,
filtering out all hardcoded auto-approved tools defined in agent.hooks.hitl_hook.
"""

import os
import sys
from typing import List, Tuple

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)


def get_non_hardcoded_mcp_tools() -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Extracts all MCP tools for GitHub, SAM CLI, and Text Editor,
    and filters out any hardcoded tools defined in agent.hooks.hitl_hook.
    """
    try:
        from agent.hooks.hitl_hook import DEFAULT_AUTO_APPROVED_TOOLS
    except Exception:
        DEFAULT_AUTO_APPROVED_TOOLS = {
            "api_manager", "call_api_manager", "sam_cli_agent", "call_sam_cli_agent",
            "REST_Agent", "call_rest_agent", "github_agent", "call_github_agent",
            "skills", "load_skill", "agent_skills", "search_code", "search_repositories",
            "get_file_contents", "search_memory", "add_memory", "sam init", "sam build",
            "sam local invoke", "create_text_file", "get_text_file_contents",
            "insert_text_file_contents", "append_text_file_contents", "patch_text_file_contents"
        }

    # Full GitHub MCP Catalog
    github_catalog = [
        ("create_pull_request", "Creates a new pull request for branch merge"),
        ("merge_pull_request", "Merges a pull request into base branch"),
        ("create_issue", "Creates a new issue in repository"),
        ("list_issues", "Lists issues filtered by state / labels"),
        ("get_issue", "Fetches detailed issue information"),
        ("update_issue", "Modifies issue title, body, or state"),
        ("add_issue_comment", "Adds discussion comment to issue/PR"),
        ("create_branch", "Creates a new branch from a commit SHA"),
        ("list_branches", "Lists repository branches"),
        ("create_commit", "Creates a new Git commit"),
        ("list_commits", "Lists recent commit history"),
        ("create_or_update_file_contents", "Writes or updates file on GitHub"),
        ("delete_file", "Deletes a repository file via Git API"),
        ("fork_repository", "Forks repository to user account"),
        ("create_repository", "Creates a new GitHub repository"),
        ("search_code", "[HARDCODED SAFE] Code reconnaissance search"),
        ("search_repositories", "[HARDCODED SAFE] Repository query search"),
        ("get_file_contents", "[HARDCODED SAFE] Reads remote file content"),
    ]

    # Full SAM CLI MCP Catalog
    samcli_catalog = [
        ("sam deploy", "Deploys CloudFormation stack to AWS"),
        ("sam sync", "Syncs local changes directly to AWS Cloud"),
        ("sam delete", "Deletes deployed AWS CloudFormation stack"),
        ("sam package", "Packages artifacts and uploads to Amazon S3"),
        ("sam validate", "Validates SAM template syntax and schema"),
        ("sam logs", "Fetches CloudWatch logs for Lambda functions"),
        ("sam list", "Lists endpoints and resources in stack"),
        ("sam pipeline init", "Generates CI/CD deployment pipelines"),
        ("sam traces", "Fetches AWS X-Ray telemetry traces"),
        ("sam init", "[HARDCODED SAFE] Scaffolds local SAM project"),
        ("sam build", "[HARDCODED SAFE] Builds Serverless artifacts"),
        ("sam local invoke", "[HARDCODED SAFE] Tests Lambda locally"),
    ]

    # Full Text Editor MCP Catalog
    text_editor_catalog = [
        ("delete_text_file_contents", "Deletes lines or file contents (Destructive)"),
        ("undo_text_file_contents", "Reverts previous file patch operations"),
        ("list_directory_contents", "Lists local directory tree"),
        ("move_text_file", "Moves or renames local source files"),
        ("copy_text_file", "Copies local files to target path"),
        ("create_text_file", "[HARDCODED SAFE] Scaffolds new text file"),
        ("get_text_file_contents", "[HARDCODED SAFE] Reads local file content"),
        ("insert_text_file_contents", "[HARDCODED SAFE] Inserts lines into file"),
        ("append_text_file_contents", "[HARDCODED SAFE] Appends lines to file"),
        ("patch_text_file_contents", "[HARDCODED SAFE] In-place diff patch"),
    ]

    # Filter out all auto-approved hardcoded tools
    github_filtered = [item for item in github_catalog if item[0] not in DEFAULT_AUTO_APPROVED_TOOLS]
    samcli_filtered = [item for item in samcli_catalog if item[0] not in DEFAULT_AUTO_APPROVED_TOOLS]
    text_editor_filtered = [item for item in text_editor_catalog if item[0] not in DEFAULT_AUTO_APPROVED_TOOLS]

    return github_filtered, samcli_filtered, text_editor_filtered
