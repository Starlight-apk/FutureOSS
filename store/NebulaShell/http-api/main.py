
    def __init__(self):
        self.server = None
        self.router = Router()
        self.middleware = MiddlewareChain()

    def init(self, deps: dict = None):
        self.server.start()

    def stop(self):
        return Response(
            status=200,
            body=json.dumps({"status": "ok", "service": "http-api"}),
            headers={"Content-Type": "application/json"}
        )

    def _server_info_handler(self, request):
        return Response(
            status=200,
            body=json.dumps({"status": "running", "plugins_loaded": True}),
            headers={"Content-Type": "application/json"}
        )


register_plugin_type("HttpApiPlugin", HttpApiPlugin)


def New():
    return HttpApiPlugin()
