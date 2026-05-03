class WsApiPlugin:
    def __init__(self):
        self._running = False

    def init(self, deps: dict = None):
        self._running = True
        Log.info("ws-api", "已启动")

    def stop(self):
        pass
