    type: str
    client: Any = None
    path: str = ""
    message: str = ""
    context: dict[str, Any] = field(default_factory=dict)


EVENT_CONNECT = "ws.connect"
EVENT_DISCONNECT = "ws.disconnect"
EVENT_MESSAGE = "ws.message"
EVENT_ERROR = "ws.error"
EVENT_SUBSCRIBE = "ws.subscribe"
EVENT_UNSUBSCRIBE = "ws.unsubscribe"
EVENT_BROADCAST = "ws.broadcast"
