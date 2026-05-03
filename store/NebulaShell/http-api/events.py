class ApiEvent:
    type: str
    request: Any = None
    response: Any = None
    error: Exception = None
    context: dict[str, Any] = field(default_factory=dict)
