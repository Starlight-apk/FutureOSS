    def __init__(self, path: str, handler: Callable):
        self.path = path
        self.handler = handler


class WsRouter:
        self.routes[path] = WsRoute(path, handler)

    async def handle(self, client: WsClient, path: str, message: str):
