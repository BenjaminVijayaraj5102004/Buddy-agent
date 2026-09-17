import os
from pathlib import Path
from typing import Any, Optional
import boto3
from strands.session import FileSessionManager, S3SessionManager
from agent.config import settings

DEFAULT_SESSIONS_DIR = os.path.abspath("./agent/memory")


def get_session_manager(
    session_id: str = "file-session",
    storage_dir: str | Path = DEFAULT_SESSIONS_DIR,
) -> FileSessionManager:
    """Create and return a FileSessionManager configured for local file persistence."""
    storage_dir_str = str(storage_dir)
    os.makedirs(storage_dir_str, exist_ok=True)
    return FileSessionManager(
        session_id=session_id,
        storage_dir=storage_dir_str,
    )


def get_s3_session_manager(
    session_id: str = "s3-session",
    bucket: Optional[str] = None,
    prefix: Optional[str] = None,
    region_name: Optional[str] = None,
    boto_session: Optional[boto3.Session] = None,
    **kwargs: Any,
) -> S3SessionManager:
    """Create and return an S3SessionManager configured for AWS S3 bucket persistence."""
    bucket_name = bucket or settings.AWS_S3_SESSION_BUCKET_NAME
    prefix_path = prefix if prefix is not None else settings.AWS_S3_SESSION_PREFIX
    region = region_name or settings.AWS_REGION

    if not bucket_name:
        raise ValueError("AWS_S3_SESSION_BUCKET_NAME is not configured in settings or .env.")

    if boto_session is None:
        session_kwargs: dict[str, Any] = {}
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        if settings.AWS_SESSION_TOKEN:
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
