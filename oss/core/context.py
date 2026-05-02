    
    Provides access to configuration, state, and utilities during plugin execution.
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._state: Dict[str, Any] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)
    
    def __repr__(self) -> str:
        return f"Context(config={self.config})"


__all__ = ['Context']
