from strands.session import FileSessionManager


session_manager = FileSessionManager(
    session_id="file-session",
    storage_dir="./agent/memory/session-memory/sessions",
)


