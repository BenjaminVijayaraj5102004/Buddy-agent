"""
Session State Management for Buddy Agent UI
Tracks active session ID, token metrics, model configuration, and manages the real agent instance.
"""

import uuid
import os
import sys
from typing import Optional, List, Dict, Any

BUDDY_AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BUDDY_AGENT_ROOT not in sys.path:
    sys.path.insert(0, BUDDY_AGENT_ROOT)

from .config import MODELS_CATALOG


class SessionState:
    def __init__(self, session_id: Optional[str] = None, model_key: Optional[str] = None, theme: str = "igi"):
        self.session_id = session_id or str(uuid.uuid4())
        
        # Check if an existing session has a persisted model_key and subagent_models
        saved_model_key = None
        saved_subagents = {}
        if session_id:
            try:
                from agent.memory import get_session_model_key, get_session_subagent_models
                saved_model_key = get_session_model_key(session_id)
                saved_subagents = get_session_subagent_models(session_id)
            except Exception:
                pass

        self.model_key = model_key or saved_model_key or "groq"
        self.subagent_models: Dict[str, str] = {
            "main": self.model_key,
            "api": saved_subagents.get("api", self.model_key),
            "github": saved_subagents.get("github", self.model_key),
            "sam": saved_subagents.get("sam", self.model_key),
        }
        if saved_subagents:
            self.subagent_models.update(saved_subagents)

        self.theme = theme
        self.empathy_enabled = True
        self.autosave_enabled = True
        self.default_mission = "FastAPI"
        self.sound_enabled = False
        self.radar_interval = 1.0
        self.braille_graphs = True
        self.per_core_threat = True
        self.bandwidth_telemetry = True
        self.messages_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.history: List[Dict[str, Any]] = []
        self._agent_instance = None
        self._agent_session_id = None
        self._agent_model_key = None

    def get_model_info(self, key: Optional[str] = None) -> Dict[str, Any]:
        target_key = (key or self.model_key).strip()
        for m in MODELS_CATALOG:
            if (
                m["key"].lower() == target_key.lower()
                or m["id"] == target_key
                or m.get("model_id", "").lower() == target_key.lower()
                or target_key.lower() in m["name"].lower()
            ):
                return m
        # Custom BYOM model format
        if ":" in target_key:
            prov, mid = target_key.split(":", 1)
            return {
                "id": "custom",
                "key": target_key,
                "model_id": mid,
                "name": f"{prov.capitalize()} - {mid} (Custom)",
                "provider": prov.capitalize(),
                "cost": "Custom",
                "context": "Variable",
                "recommended": False,
            }
        return MODELS_CATALOG[0]

    def get_subagent_model_info(self, agent_name: str) -> Dict[str, Any]:
        """Returns model metadata for a specific sub-agent ('main', 'api', 'github', 'sam')."""
        key = self.subagent_models.get(agent_name, self.model_key)
        return self.get_model_info(key)

    def get_agent(self):
        """Returns or instantiates the real Strands Agent for this session & multi-agent models."""
        if (
            self._agent_instance is not None
            and self._agent_session_id == self.session_id
            and self._agent_model_key == self.model_key
        ):
            return self._agent_instance

        try:
            import dotenv
            env_path = os.path.join(BUDDY_AGENT_ROOT, ".env")
            if os.path.exists(env_path):
                dotenv.load_dotenv(env_path)
        except Exception:
            pass

        if BUDDY_AGENT_ROOT not in sys.path:
            sys.path.insert(0, BUDDY_AGENT_ROOT)

        from buddy.buddy import create_buddy_agent
        
        self._agent_instance = create_buddy_agent(
            session_id=self.session_id,
            model_choice=self.model_key,
            subagent_models=self.subagent_models,
        )
        self._agent_session_id = self.session_id
        self._agent_model_key = self.model_key
        return self._agent_instance

    def reset_agent(self):
        """Resets the cached agent instance so it is re-instantiated on next use."""
        self._agent_instance = None
        self._agent_session_id = None
        self._agent_model_key = None

    def switch_model(self, model_key: str, agent_name: Optional[str] = None):
        """Switches the active model for this session or a specific subagent, and resets the agent."""
        if agent_name and agent_name in ("api", "github", "sam"):
            self.subagent_models[agent_name] = model_key
        elif agent_name == "all":
            self.model_key = model_key
            self.subagent_models = {
                "main": model_key,
                "api": model_key,
                "github": model_key,
                "sam": model_key,
            }
        else:
            self.model_key = model_key
            self.subagent_models["main"] = model_key

        self.reset_agent()
        try:
            from agent.memory import set_session_model_key, set_session_subagent_models
            set_session_model_key(self.session_id, self.model_key)
            set_session_subagent_models(self.session_id, self.subagent_models)
        except Exception:
            pass

    def switch_session(self, session_id: str, model_key: Optional[str] = None):
        """Switches to an existing or new session, restoring its models unless overridden."""
        self.session_id = session_id
        if model_key:
            self.model_key = model_key
            self.subagent_models["main"] = model_key
        else:
            try:
                from agent.memory import get_session_model_key, get_session_subagent_models
                saved = get_session_model_key(session_id)
                if saved:
                    self.model_key = saved
                saved_sub = get_session_subagent_models(session_id)
                if saved_sub:
                    self.subagent_models = saved_sub
                else:
                    self.subagent_models = {
                        "main": self.model_key,
                        "api": self.model_key,
                        "github": self.model_key,
                        "sam": self.model_key,
                    }
            except Exception:
                pass
        self.reset_agent()
        try:
            from agent.memory import set_current_session_id, set_session_model_key, set_session_subagent_models
            set_current_session_id(session_id)
            set_session_model_key(session_id, self.model_key)
            set_session_subagent_models(session_id, self.subagent_models)
        except Exception:
            pass


active_session = SessionState()

