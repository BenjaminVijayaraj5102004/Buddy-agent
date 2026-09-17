from strands import Agent
from strands.tools import tool
from agent.model import model
from agent.memory import memory_manager, get_session_manager
from agent.services.api_manager import API_MANAGER
from agent.guardrils import BUDDY_AGENT_PROMPT
import agent.trace


@tool(
    name="api_manager",
    description="Delegates all API-related tasks (REST API endpoint creation, route definitions, schemas) to the API Manager.",
)
def call_api_manager(task_description: str) -> str:
    """Delegates API design, endpoint generation, and schema tasks to the API Manager."""
    response = API_MANAGER(task_description)
    return str(response)


buddy_agent = Agent(
    name="Buddy",
    model=model,
    tools=[call_api_manager],
    memory_manager=memory_manager,
    session_manager=get_session_manager("buddy-main-session"),
    system_prompt=BUDDY_AGENT_PROMPT,
)


def main():
    """Interactive CLI runner for Buddy Agent."""
    print("=" * 50)
    print("🤖 Buddy Agent Initialized")
    print("Type your request or 'exit'/'quit' to stop.")
    print("=" * 50 + "\n")

    while True:
        try:
            prompt = input("You > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "q"):
                print("👋 Goodbye!")
                break

            result = buddy_agent(prompt)
            print(f"\nBuddy >\n{result}\n")
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()