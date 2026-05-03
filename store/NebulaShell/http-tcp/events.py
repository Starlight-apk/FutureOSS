class TcpEvent:
    type: str
    client: Any = None
    data: bytes = b""
    context: dict[str, Any] = field(default_factory=dict)


EVENT_CONNECT = "tcp.connect"
EVENT_DISCONNECT = "tcp.disconnect"
EVENT_DATA = "tcp.data"
EVENT_REQUEST = "tcp.http.request"
EVENT_RESPONSE = "tcp.http.response"
EVENT_ERROR = "tcp.error"
