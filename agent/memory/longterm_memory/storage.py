import asyncio
import os
from pathlib import Path
from typing import Any, Optional

from strands.memory import MemoryManager
from strands.storage import LocalFileStorage
from strands.vended_memory_stores.file_memory_store import FileMemoryStore
from strands.vended_memory_stores.bedrock_knowledge_base import (
    BedrockKnowledgeBaseConfig,
    BedrockKnowledgeBaseStore,
)
from agent.config import settings

DEFAULT_MEMORY_DIR = os.path.abspath("./agent/memory")


def get_longterm_storage(base_dir: str | Path = DEFAULT_MEMORY_DIR) -> LocalFileStorage:
    """Initialize and return a LocalFileStorage instance for persisting data locally."""
    base_dir_str = str(base_dir)
    os.makedirs(base_dir_str, exist_ok=True)
    return LocalFileStorage(base_dir=base_dir_str)


def get_longterm_store(
    name: str = "buddy_longterm_memory",
    base_dir: str | Path = DEFAULT_MEMORY_DIR,
    writable: bool = True,
    description: str = "Local long-term memory for persisting user preferences, facts, and session summaries.",
) -> FileMemoryStore:
    """Create and return a FileMemoryStore configured with local file storage."""
    storage = get_longterm_storage(base_dir=base_dir)
    return FileMemoryStore(  # type: ignore[abstract]
        name=name,
        storage=storage,
        writable=writable,
        description=description,
    )


def get_bedrock_kb_store(
    name: str = "buddy_bedrock_kb_memory",
    knowledge_base_id: Optional[str] = None,
    data_source_id: Optional[str] = None,
    data_source_type: str = "CUSTOM",
    region_name: Optional[str] = None,
    writable: bool = True,
    description: str = "Amazon Bedrock Knowledge Base long-term memory for semantic knowledge retrieval and persistence.",
    **kwargs: Any,
) -> BedrockKnowledgeBaseStore:
    """Create and return a BedrockKnowledgeBaseStore configured for Amazon Bedrock Knowledge Base."""
    kb_id = knowledge_base_id or settings.BEDROCK_KNOWLEDGE_BASE_ID
    ds_id = data_source_id or settings.BEDROCK_KB_DATA_SOURCE_ID
    region = region_name or settings.AWS_REGION

    if not kb_id:
        raise ValueError("BEDROCK_KNOWLEDGE_BASE_ID is not configured in settings or .env.")

    config_kwargs: dict[str, Any] = {
        "knowledge_base_id": kb_id,
        "region_name": region,
        "data_source_type": data_source_type,
    }
    if ds_id:
        config_kwargs["data_source_id"] = ds_id
    elif writable:
        config_kwargs["data_source_id"] = "default-data-source"
    config_kwargs.update(kwargs)

    kb_config = BedrockKnowledgeBaseConfig(**config_kwargs)

    return BedrockKnowledgeBaseStore(
        name=name,
        config=kb_config,
        writable=writable,
        description=description,
    )


def get_memory_manager(
    stores: list[Any] | None = None,
    search_tool_config: bool = True,
    add_tool_config: bool = True,
    injection: bool = True,
) -> MemoryManager:
    """Create and return a MemoryManager for agent interactions."""
    if stores is None:
        stores = [longterm_store]
    return MemoryManager(
        stores=stores,
        search_tool_config=search_tool_config,
        add_tool_config=add_tool_config,
        injection=injection,
    )


# Default local storage and long-term memory store instances
longterm_storage = get_longterm_storage()
longterm_store = get_longterm_store()
memory_manager = get_memory_manager()


async def add_memory_entry(
    content: str,
    metadata: dict[str, Any] | None = None,
    store: Any | None = None,
) -> Any:
    """Add a memory entry to the long-term store asynchronously."""
    target_store = store or longterm_store
    return await target_store.add(content=content, metadata=metadata)


def add_memory_entry_sync(
    content: str,
    metadata: dict[str, Any] | None = None,
    store: Any | None = None,
) -> Any:
    """Synchronous helper to add a memory entry to the long-term store."""
    return asyncio.run(add_memory_entry(content=content, metadata=metadata, store=store))


async def search_memory_entries(
    query: str,
    store: Any | None = None,
) -> list[Any]:
    """Search for relevant memory entries in the long-term store asynchronously."""
    target_store = store or longterm_store
    return await target_store.search(query=query)


def search_memory_entries_sync(
    query: str,
    store: Any | None = None,
) -> list[Any]:
    """Synchronous helper to search memory entries in the long-term store."""
    return asyncio.run(search_memory_entries(query=query, store=store))


async def save_session_to_longterm(
    session_id: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    store: Any | None = None,
) -> Any:
    """Save insights, summaries, or messages from a session into the long-term memory store."""
    meta = {"session_id": session_id, "type": "session_summary"}
    if metadata:
        meta.update(metadata)
    return await add_memory_entry(content=content, metadata=meta, store=store)


def save_session_to_longterm_sync(
    session_id: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    store: Any | None = None,
) -> Any:
    """Synchronous helper to save session memory into long-term memory."""
    return asyncio.run(
        save_session_to_longterm(
            session_id=session_id,
            content=content,
            metadata=metadata,
            store=store,
        )
    )
