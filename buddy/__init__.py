def __getattr__(name: str):
    if name in ("buddy_agent", "call_api_manager", "main"):
        from buddy import buddy as _buddy
        return getattr(_buddy, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["buddy_agent", "call_api_manager", "main"]
