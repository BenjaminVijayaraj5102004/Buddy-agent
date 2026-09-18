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
    def __init__(self, session_id: Optional[str] = None, model_key: str = "groq", theme: str = "igi"):
        self.session_id = session_id or str(uuid.uuid4())
        self.model_key = model_key
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

    def get_model_info(self) -> Dict[str, Any]:
        for m in MODELS_CATALOG:
            if m["key"] == self.model_key or m["id"] == self.model_key or self.model_key.lower() in m["name"].lower():
                return m
        return MODELS_CATALOG[0]

    def get_agent(self):
        """Returns or instantiates the real Strands Agent for this session & model."""
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
        
        try:
            self._agent_instance = create_buddy_agent(session_id=self.session_id, model_choice=self.model_key)
            self._agent_session_id = self.session_id
            self._agent_model_key = self.model_key
            return self._agent_instance
        except Exception as e:
            if self.model_key != "groq":
                self._agent_instance = create_buddy_agent(session_id=self.session_id, model_choice="groq")
                self._agent_session_id = self.session_id
                self._agent_model_key = "groq"
                self.model_key = "groq"
                return self._agent_instance
            raise e

    def reset_agent(self):
        """Resets the cached agent instance so it is re-instantiated on next use."""
        self._agent_instance = None
        self._agent_session_id = None
        self._agent_model_key = None


active_session = SessionState()
