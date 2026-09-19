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

)
from agent.services import API_MANAGER, sam_cli_agent, github_agent
from agent.services.api_agent.REST import rest_agent
from agent.guardrils import BUDDY_AGENT_PROMPT
from agent.hooks import HumanInTheLoopHook
from agent.skills import buddy_agent_skills


@tool(name="api_manager", description="Delegates all API-related tasks (REST API endpoint creation, route definitions, schemas) to the API Manager.")
def call_api_manager(task_description: str) -> str:
    """Delegates API design, endpoint generation, and schema tasks to the API Manager."""
    import os
    cwd = os.path.abspath(os.getcwd())
    full_task = f"{task_description}\n[Workspace Directory: {cwd}]"
    try:
        response = API_MANAGER(full_task)
        return str(response)
    except Exception as e:
        return f"Error executing API_MANAGER: {e}"


@tool(name="sam_cli_agent", description="Delegates all AWS SAM-related tasks (SAM init, SAM deploy) to the SAM CLI Agent.")
def call_sam_cli_agent(task_description: str) -> str:
    import os
    cwd = os.path.abspath(os.getcwd())
    full_task = f"{task_description}\n[Workspace Directory: {cwd}]"
    try:
        response = sam_cli_agent(full_task)
        return str(response)
    except Exception as e:
        return f"Error executing sam_cli_agent: {e}"


@tool(name="github_agent", description="Delegates all GitHub operations (issues, pull requests, branches, commits, repo metadata) to the GitHub Agent.")
def call_github_agent(task_description: str) -> str:
    try:
        response = github_agent(task_description)
        return str(response)
    except Exception as e:
        return f"Error executing github_agent: {e}"


def create_buddy_agent(
    session_id: str | None = None,
    model_choice: str | None = None,
    subagent_models: dict[str, str] | None = None,
) -> Agent:
    """Creates a Buddy Agent instance attached to a specific session ID and chosen model(s),
    supporting independent model assignment for main orchestrator and each sub-agent
    (API_MANAGER, rest_agent, sam_cli_agent, github_agent).
    """
    sid = session_id or get_current_session_id()
    set_current_session_id(sid)

    # If no model_choice was passed, check if the session already has saved model configurations
    saved_subagent_models: dict[str, str] = {}
    try:
        from agent.memory import get_session_model_key, get_session_subagent_models
        if not model_choice:
            saved_model = get_session_model_key(sid)
            if saved_model:
                model_choice = saved_model
        saved_subagent_models = get_session_subagent_models(sid)
    except Exception:
        pass

    # Merge subagent models (explicit passed > saved in session > fallback to main model)
    active_subagents = dict(saved_subagent_models)
    if subagent_models:
        active_subagents.update(subagent_models)

    main_choice = model_choice or active_subagents.get("main") or "groq"
    api_choice = active_subagents.get("api") or active_subagents.get("rest") or main_choice
    sam_choice = active_subagents.get("sam") or main_choice
    github_choice = active_subagents.get("github") or main_choice

    # Route and instantiate models for each agent independently
    selected_main_model = route_model(main_choice)
    selected_api_model = route_model(api_choice)
    selected_sam_model = route_model(sam_choice)
    selected_github_model = route_model(github_choice)

    # Persist the active models for this session
    try:
        from agent.memory import set_session_model_key, set_session_subagent_models
        set_session_model_key(sid, main_choice)
        set_session_subagent_models(sid, {
            "main": main_choice,
            "api": api_choice,
            "sam": sam_choice,
            "github": github_choice,
        })
    except Exception:
        pass

    # Dynamically propagate the specific selected model and session to each sub-agent
    session_mgr = get_session_manager(sid)
    API_MANAGER.model = selected_api_model
    rest_agent.model = selected_api_model
    sam_cli_agent.model = selected_sam_model
    github_agent.model = selected_github_model

    return Agent(
        name="Buddy",
        model=selected_main_model,
        tools=[call_api_manager, call_sam_cli_agent, call_github_agent],
        plugins=[buddy_agent_skills],
        hooks=[HumanInTheLoopHook()],
        session_manager=session_mgr,
        system_prompt=BUDDY_AGENT_PROMPT,
        conversation_manager=SafeSlidingWindowConversationManager(
            window_size=5,
            should_truncate_results=True,
        ),
    )


# Default instance for direct module imports
buddy_agent = create_buddy_agent()


def _resolve_model_prompt_choice(choice_input: str, default_fallback: str = "groq") -> str:
    """Helper to resolve a model input string or BYOM custom setup."""
    raw = choice_input.strip()
    if not raw:
        return default_fallback
    if raw in ("8", "byom", "custom"):
        try:
            print("\n   🔧 Bring Your Own Model (BYOM) Setup:")
            prov_input = input("      Select Provider [1: Groq, 2: Ollama, 3: Bedrock, default: Groq]: ").strip().lower()
            custom_prov = "ollama" if prov_input in ("2", "ollama") else ("bedrock" if prov_input in ("3", "bedrock") else "groq")
            custom_mid = input(f"      Enter Custom Model ID for {custom_prov.upper()}: ").strip()
            return f"{custom_prov}:{custom_mid}" if custom_mid else custom_prov
        except (KeyboardInterrupt, EOFError):
            return default_fallback
    return raw


def main():
    """Interactive CLI runner for Buddy Agent with multi-agent dynamic model routing & UUID session support."""
    print("=" * 65)
    print("🤖 Buddy Agent Initialized — Tactical Multi-Agent Orchestrator")
    print("=" * 65)

    # 1. Model Selection
    print("🧠 Select AI Model for Main Orchestrator (Buddy):")
    print("   ── Groq Cloud ────────────────────────────────────────")
    print("   [1] Groq Cloud: Qwen 3.8 27B (Default)")
    print("   [2] Groq Cloud: GPT-OSS 120B")
    print("   [3] Groq Cloud: Llama Prompt Guard 2 22M")
    print("   ── Ollama Local ──────────────────────────────────────")
    print("   [4] Ollama Local: Llama 3.1 8B (Default)")
    print("   [5] Ollama Local: Qwen 7B")
    print("   [6] Ollama Local: Qwen 2.5 Coder 32B")
    print("   ── AWS Bedrock ───────────────────────────────────────")
    print("   [7] AWS Bedrock: Claude 3.7 Sonnet")
    print("   ── Bring Your Own Model ─────────────────────────────")
    print("   [8] Bring Your Own Model (BYOM - Custom ID)")
    print("-" * 65)

    try:
        user_choice_input = input("Enter choice for Main Agent [1-8, name, or Enter for Default]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Exiting...")
        return

    main_model_choice = _resolve_model_prompt_choice(user_choice_input, default_fallback="groq")
    main_model_info = get_model_info(main_model_choice)
    print(f"✅ Main Agent Model : {main_model_info['name']}")

    # 2. Granular Sub-Agent Model Customization
    subagent_models: dict[str, str] = {
        "main": main_model_choice,
        "api": main_model_choice,
        "sam": main_model_choice,
        "github": main_model_choice,
    }

    try:
        custom_sub = input("\n🎯 Customize sub-agent models (REST API, GitHub, SAM CLI)? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Exiting...")
        return

    if custom_sub in ("y", "yes"):
        print("\n⚙️  Configure Sub-Agent Satellites:")
        # REST API Agent
        try:
            api_in = input(f"   [1/3] REST API Agent   [1-8/name or Enter to use '{main_model_info['name']}']: ").strip()
            if api_in:
                subagent_models["api"] = _resolve_model_prompt_choice(api_in, default_fallback=main_model_choice)

            # GitHub Agent
            gh_in = input(f"   [2/3] GitHub Agent     [1-8/name or Enter to use '{main_model_info['name']}']: ").strip()
            if gh_in:
                subagent_models["github"] = _resolve_model_prompt_choice(gh_in, default_fallback=main_model_choice)

            # SAM CLI Agent
            sam_in = input(f"   [3/3] SAM CLI Agent    [1-8/name or Enter to use '{main_model_info['name']}']: ").strip()
            if sam_in:
                subagent_models["sam"] = _resolve_model_prompt_choice(sam_in, default_fallback=main_model_choice)
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting...")
            return

    # Print Multi-Agent Topology Summary
    api_info = get_model_info(subagent_models["api"])
    gh_info = get_model_info(subagent_models["github"])
    sam_info = get_model_info(subagent_models["sam"])

    print("\n" + "=" * 65)
    print("🛰️  Active Multi-Agent Model Topology:")
    print(f"   🤖 Main Orchestrator (Buddy) : {main_model_info['name']}")
    print(f"   ⚡ REST API Agent            : {api_info['name']}")
    print(f"   🐙 GitHub Agent              : {gh_info['name']}")
    print(f"   📦 SAM CLI Deploy Agent      : {sam_info['name']}")
    print("=" * 65)

    # 3. Session Selection
    try:
        user_input_session = input("\nEnter Session ID to resume (or press Enter for new session): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Exiting...")
        return

    if user_input_session:
        session_id = set_current_session_id(user_input_session)
        print(f"🔄 Resuming session: {session_id}")
    else:
        session_id = generate_new_session_id()
        print(f"✨ New session created: {session_id}")

    # 4. Instantiate Agent with multi-agent models & session
    active_agent = create_buddy_agent(
        session_id=session_id,
        model_choice=main_model_choice,
        subagent_models=subagent_models,
    )

    # Show count of restored messages if resuming
    if active_agent.messages:
        print(f"📁 Loaded {len(active_agent.messages)} previous message(s) from session history.")

    print("=" * 65)
    print(f"📌 Active Session ID: {session_id}")
    print("💬 Type your request or 'exit' / 'quit' / 'q' to stop.")
    print("=" * 65 + "\n")

    while True:
        try:
            prompt = input("You > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "q"):
                break

            result = active_agent(prompt)
            print(f"\nBuddy > {result}\n")
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

    print("\n" + "=" * 65)
    print("💾 Session Saved!")
    print(f"🔑 Session ID: {session_id}")
    print("📋 Copy and paste this ID next time to resume your conversation.")
    print("👋 Goodbye!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()