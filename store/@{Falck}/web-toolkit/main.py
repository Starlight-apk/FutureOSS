
    def __init__(self):
        self.router = None
        self.static_handler = None
        self.template_engine = None
        self.http_api = None
        self.http_tcp = None
        self.storage = None
        self.config = {}        self.root_dir = None

    def init(self, deps: dict = None):
        if self.http_api:
            http_instance = self.http_api
            if hasattr(http_instance, "router"):
                http_instance.router.get(
                    self.config.get("website_prefix", "/website") + "/",
                    self._serve_website_index
                )
                http_instance.router.get(
                    self.config.get("website_prefix", "/website") + "/:path",
                    self._serve_static
                )
                http_instance.router.get(
                    self.config.get("static_prefix", "/static") + "/:path",
                    self._serve_static
                )

        if self.http_tcp:
            tcp_instance = self.http_tcp
            if hasattr(tcp_instance, "router"):
                tcp_instance.router.get(
                    self.config.get("website_prefix", "/website") + "/",
                    self._serve_website_index
                )
                tcp_instance.router.get(
                    self.config.get("website_prefix", "/website") + "/:path",
                    self._serve_static
                )
                tcp_instance.router.get(
                    self.config.get("static_prefix", "/static") + "/:path",
                    self._serve_static
                )

        _Log.info("Web 工具包已启动")

    def stop(self):
        self.http_api = instance

    def set_http_tcp(self, instance):
        self.storage = instance

    def set_static_dir(self, path: str):
        template_root = Path(path)
        if template_root.exists():
            self.template_engine.set_root(str(template_root))

    def _load_config(self):
        index_file = self.config.get("index_file", "index.html")
        if self.root_dir:
            path = self.root_dir / index_file
            if path.exists():
                content = path.read_text(encoding="utf-8")
                return Response(
                    status=200,
                    headers={"Content-Type": "text/html; charset=utf-8"},
                    body=content
                )
        return Response(status=404, body="Index file not found")

    def _serve_static(self, request):
