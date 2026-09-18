from typing import Any
import agent.trace
from strands import Agent
from strands.tools import tool
from strands.agent.conversation_manager import (
    SlidingWindowConversationManager,
    SummarizingConversationManager,
)
from strands.types.content import Message
from agent.model import (
    get_model_info,
    list_available_models,
    route_model,
)
from agent.memory import (
    get_session_manager,
    get_current_session_id,
    set_current_session_id,
    generate_new_session_id,
    list_stored_sessions,
    SafeSlidingWindowConversationManager,
    SafeSummarizingConversationManager,
)
from agent.services import API_MANAGER, sam_cli_agent, github_agent
from agent.guardrils import BUDDY_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import buddy_agent_skills
from agent.state import BuddyAgentOutput



@tool(name="api_manager", description="Delegates all API-related tasks (REST API endpoint creation, route definitions, schemas) to the API Manager.")
def call_api_manager(task_description: str) -> str:
    """Delegates API design, endpoint generation, and schema tasks to the API Manager."""
    import os
    cwd = os.path.abspath(os.getcwd())
    full_task = f"{task_description}\n[Workspace Directory: {cwd}]"
    response = API_MANAGER(full_task)
    return str(response)


@tool(name="sam_cli_agent", description="Delegates all AWS SAM-related tasks (SAM init, SAM deploy) to the SAM CLI Agent.")
def call_sam_cli_agent(task_description: str) -> str:
    import os
    cwd = os.path.abspath(os.getcwd())
    full_task = f"{task_description}\n[Workspace Directory: {cwd}]"
    response = sam_cli_agent(full_task)
    return str(response)


@tool(name="github_agent", description="Delegates all GitHub operations (issues, pull requests, branches, commits, repo metadata) to the GitHub Agent.")
def call_github_agent(task_description: str) -> str:
    response = github_agent(task_description)
    return str(response)


def create_buddy_agent(
    session_id: str | None = None,
    model_choice: str | None = None,
) -> Agent:
    """Creates a Buddy Agent instance attached to a specific session ID and chosen model."""
    sid = session_id or get_current_session_id()
    selected_model = route_model(model_choice)
    return Agent(
        name="Buddy",
        model=selected_model,
        tools=[call_api_manager, call_sam_cli_agent, call_github_agent],
        plugins=[buddy_agent_skills],
        hooks=[HumanInTheLoopHook()],
        session_manager=get_session_manager(sid),
        system_prompt=BUDDY_AGENT_PROMPT,
        conversation_manager=SafeSlidingWindowConversationManager(
            window_size=5,
            should_truncate_results=True,
        ),
    )


# Default instance for direct module imports
buddy_agent = create_buddy_agent()


def main():
    """Interactive CLI runner for Buddy Agent with dynamic model routing & UUID session support."""
    print("=" * 60)
    print("🤖 Buddy Agent Initialized")
    print("=" * 60)

    # 1. Model Selection
    print("🧠 Select AI Model:")
    available_models = list_available_models()
    for m in available_models:
        default_tag = " (Default)" if m["key"] == "groq" else ""
        print(f"   [{m['id']}] {m['name']}{default_tag}")
    print("-" * 60)

    try:
        user_model_choice = input("Enter model choice [1-3, name, or Enter for Groq]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Exiting...")
        return

    model_info = get_model_info(user_model_choice)
    print(f"✅ Selected Model: {model_info['name']}")
    print("-" * 60)

    # 2. Session Selection
    try:
        user_input_session = input("Enter Session ID to resume (or press Enter for new session): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Exiting...")
        return

    if user_input_session:
        session_id = set_current_session_id(user_input_session)
        print(f"🔄 Resuming session: {session_id}")
    else:
        session_id = generate_new_session_id()
        print(f"✨ New session created: {session_id}")

    # 3. Instantiate Agent with chosen model & session
    active_agent = create_buddy_agent(session_id=session_id, model_choice=user_model_choice)

    # Show count of restored messages if resuming
    if active_agent.messages:
        print(f"📁 Loaded {len(active_agent.messages)} previous message(s) from session history.")

    print("=" * 60)
    print(f"📌 Active Model     : {model_info['name']}")
    print(f"📌 Active Session ID: {session_id}")
    print("💬 Type your request or 'exit' / 'quit' / 'q' to stop.")
    print("=" * 60 + "\n")

    while True:
        try:
            prompt = input("You > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "q"):
                break

            result = active_agent(prompt)
            print(f"\nBuddy >\n{result}\n")
            if hasattr(result, "metrics") and hasattr(result.metrics, "accumulated_usage"):
                input_tokens = result.metrics.accumulated_usage.get("inputTokens", 0)
                output_tokens = result.metrics.accumulated_usage.get("outputTokens", 0)
                print(f"📥 Input tokens: {input_tokens} | 📤 Output tokens: {output_tokens}")
                print(f"Total tokens: {result.metrics.accumulated_usage['totalTokens']}\n")
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

    print("\n" + "=" * 60)
    print("💾 Session Saved!")
    print(f"🔑 Session ID: {session_id}")
    print("📋 Copy and paste this ID next time to resume your conversation.")
    print("👋 Goodbye!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()