"""Skills registry and pre-configured AgentSkills plugins for specialized agents."""

from pathlib import Path
from strands import AgentSkills, Skill

SKILLS_DIR = Path(__file__).parent


def load_skill_by_name(name: str) -> Skill:
    """Load a specific Skill by its folder name."""
    skill_path = SKILLS_DIR / name
    return Skill.from_file(skill_path)


# Individual Skill instances
buddy_skill = load_skill_by_name("buddy-agent")
api_manager_skill = load_skill_by_name("api-manager")
rest_agent_skill = load_skill_by_name("rest-agent")
sam_cli_agent_skill = load_skill_by_name("sam-cli-agent")
github_agent_skill = load_skill_by_name("github-agent")

# Pre-configured AgentSkills plugins ready to attach to agents
buddy_agent_skills = AgentSkills(skills=[buddy_skill])
api_manager_skills = AgentSkills(skills=[api_manager_skill])
rest_agent_skills = AgentSkills(skills=[rest_agent_skill])
sam_cli_agent_skills = AgentSkills(skills=[sam_cli_agent_skill])
github_agent_skills = AgentSkills(skills=[github_agent_skill])

__all__ = [
    "SKILLS_DIR",
    "load_skill_by_name",
    "buddy_skill",
    "api_manager_skill",
    "rest_agent_skill",
    "sam_cli_agent_skill",
    "github_agent_skill",
    "buddy_agent_skills",
    "api_manager_skills",
    "rest_agent_skills",
    "sam_cli_agent_skills",
    "github_agent_skills",
]
