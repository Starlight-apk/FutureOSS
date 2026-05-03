class WsRoute:
    def __init__(self, path: str, handler: Callable):
        self.path = path
        self.handler = handler


class WsRouter:
    def __init__(self):
        self.routes: dict[str, WsRoute] = {}

    def add(self, path: str, handler: Callable):
        self.routes[path] = WsRoute(path, handler)

    async def handle(self, client: WsClient, path: str, message: str):
        pass
