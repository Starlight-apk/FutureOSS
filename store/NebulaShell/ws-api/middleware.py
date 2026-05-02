    async def process(self, client: Any, message: str, next_fn: Callable) -> Optional[str]:
    async def process(self, client, message, next_fn):
        return await next_fn()


class WsMiddlewareChain:
        self.middlewares.append(middleware)

    async def run(self, client, message) -> Optional[str]:
