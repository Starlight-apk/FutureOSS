
class HttpTcpPlugin:
    def __init__(self):
        self.server = None
        self.router = TcpRouter()
        self.middleware = TcpMiddlewareChain()

    def init(self, deps: dict = None):
        self.server.start()

    def stop(self):
        pass
