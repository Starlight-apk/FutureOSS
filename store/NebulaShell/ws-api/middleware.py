class WsMiddleware:
    async def process(self, client: Any, message: str, next_fn: Callable) -> Optional[str]:
        pass


class WsMiddlewareChain:
    def __init__(self):
        self.middlewares: list[WsMiddleware] = []

    def add(self, middleware: WsMiddleware):
        self.middlewares.append(middleware)

    async def run(self, client, message) -> Optional[str]:
        pass
