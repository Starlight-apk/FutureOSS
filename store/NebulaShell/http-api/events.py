    type: str    request: Any = None
    response: Any = None
    error: Exception = None
    context: dict[str, Any] = field(default_factory=dict)


class HttpEventBus:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable):
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                import traceback; print(f"[events.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
                pass

    def clear(self):
