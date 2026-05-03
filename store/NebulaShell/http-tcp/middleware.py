class TcpMiddleware:
    def process(self, request: dict, next_fn: Callable) -> Optional[dict]:
        pass


class TcpCorsMiddleware(TcpMiddleware):

    def __init__(self):
        self.middlewares: list[TcpMiddleware] = []
        self.add(TcpLogMiddleware())
        self.add(TcpCorsMiddleware())

    def add(self, middleware: TcpMiddleware):
        idx = 0

        def next_fn():
            nonlocal idx
            if idx < len(self.middlewares):
                mw = self.middlewares[idx]
                idx += 1
                return mw.process(request, next_fn)
            return None

        return next_fn()
