import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Optional
import boto3
from strands.session import FileSessionManager, S3SessionManager
from strands.types.exceptions import SessionException
from agent.config import settings

DEFAULT_SESSIONS_DIR = os.path.abspath("./agent/memory/sessions_data")

# Active global session ID (defaults to a fresh UUID)
_current_session_id: str = str(uuid.uuid4())


def get_current_session_id() -> str:
    """Get the active global session ID."""
    global _current_session_id
    return _current_session_id


def set_current_session_id(session_id: str) -> str:
    """Set the active global session ID."""
    global _current_session_id
    _current_session_id = session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())
    return _current_session_id


def generate_new_session_id() -> str:
    """Generate and set a fresh UUID session ID."""
    return set_current_session_id(str(uuid.uuid4()))


def get_session_manager(
    session_id: Optional[str] = None,
    storage_dir: str | Path = DEFAULT_SESSIONS_DIR,
) -> FileSessionManager:
    """Create and return a FileSessionManager configured for local file persistence with auto-repair."""
    sid = session_id or get_current_session_id()
    storage_dir_str = str(storage_dir)
    os.makedirs(storage_dir_str, exist_ok=True)

    session_path = os.path.join(storage_dir_str, f"session_{sid}")
    session_file = os.path.join(session_path, "session.json")


    # If the session directory exists but session.json is missing or corrupted, repair it
    if os.path.exists(session_path) and not os.path.exists(session_file):
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump({"session_id": sid, "session_type": "agent"}, f)
        except Exception:
            pass

    try:
        return FileSessionManager(
            session_id=sid,
            storage_dir=storage_dir_str,
        )
    except SessionException:
        # Directory structure existed from previous interrupted session, ensure session.json exists
        if os.path.exists(session_path) and not os.path.exists(session_file):
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump({"session_id": sid, "session_type": "agent"}, f)
        elif os.path.exists(session_path):
            # If session is irrecoverably corrupted, reset the session directory
            shutil.rmtree(session_path, ignore_errors=True)

        return FileSessionManager(
            session_id=sid,
            storage_dir=storage_dir_str,
        )



def get_s3_session_manager(
    session_id: str = "s3-session",
    bucket: Optional[str] = None,
    prefix: Optional[str] = None,
    region_name: Optional[str] = None,
    boto_session: Optional[boto3.Session] = None,
    fallback_to_local: bool = True,
    **kwargs: Any,
) -> S3SessionManager | FileSessionManager:
    """Create and return an S3SessionManager configured for AWS S3 bucket persistence.
    
    If S3 bucket access fails (e.g. AWS IAM permission issue) and fallback_to_local=True,
    it gracefully falls back to local FileSessionManager.
    """
    bucket_name = bucket or settings.AWS_S3_SESSION_BUCKET_NAME
    prefix_path = prefix if prefix is not None else settings.AWS_S3_SESSION_PREFIX
    region = region_name or settings.AWS_REGION

    if not bucket_name:
        if fallback_to_local:
            print(f"[WARN] AWS_S3_SESSION_BUCKET_NAME not configured. Falling back to local file session for '{session_id}'.")
            return get_session_manager(session_id=session_id)
        raise ValueError("AWS_S3_SESSION_BUCKET_NAME is not configured in settings or .env.")

    try:
        if boto_session is None:
            session_kwargs: dict[str, Any] = {}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            if settings.AWS_SESSION_TOKEN and not settings.AWS_SESSION_TOKEN.startswith("mock-"):
                session_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN
            if region:
                session_kwargs["region_name"] = region
            boto_session = boto3.Session(**session_kwargs)

        return S3SessionManager(
            session_id=session_id,
            bucket=bucket_name,
            prefix=prefix_path,
            boto_session=boto_session,
            region_name=region,
            **kwargs,
        )
    except Exception as e:
        if fallback_to_local:
            print(f"[WARN] S3 Session Manager initialization for '{session_id}' failed ({e}). Falling back to local file session storage.")
            return get_session_manager(session_id=session_id)
        raise


# Default local session manager instance
session_manager = get_session_manager()


def list_stored_sessions(storage_dir: str | Path = DEFAULT_SESSIONS_DIR) -> list[str]:
    """List all stored session IDs in the local session storage directory."""
    storage_path = Path(storage_dir)
    if not storage_path.exists():
        return []

    sessions = []
    for item in storage_path.iterdir():
        if item.is_dir() and item.name.startswith("session_"):
            sessions.append(item.name.replace("session_", "", 1))
    return sessions
