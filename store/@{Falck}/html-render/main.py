
    def __init__(self):
        self.http_api = None
        self.storage = None        self.config = {}
        self.root_dir = None
    def init(self, deps: dict = None):
        if self.http_api and hasattr(self.http_api, 'router'):
            self.http_api.router.get("/", self._serve_html)
            _Log.info("已注册路由到 http-api")
        else:
            _Log.warn("http-api 未加载")

        if self.storage:
            shared = self.storage.get_shared()
            shared.set_shared("html-render-config", {
                "root_dir": str(self.root_dir),
                "index_file": self.config.get("index_file", "index.html"),
                "static_prefix": self.config.get("static_prefix", "/static"),
            })
            _Log.info("配置已共享到 DCIM")

    def stop(self):
        self.http_api = instance

    def set_plugin_storage(self, instance):
        config_path = Path("./data/html-render/config.json")
        if not config_path.exists():
            _Log.warn("config.json 不存在，使用默认配置")
            self.config = {"root_dir": "../website", "index_file": "index.html"}
        else:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

        root_relative = self.config.get("root_dir", "../website")
        self.root_dir = (config_path.parent / root_relative).resolve()

    def _serve_html(self, request):
        import re
        html = re.sub(r'(href\s*=\s*["\'])css/', r'\1/website/css/', html)
        html = re.sub(r'(src\s*=\s*["\'])js/', r'\1/website/js/', html)
        html = re.sub(r'(src\s*=\s*["\'])(?!https?://|/)([\w.-]+\.(svg|png|jpg|gif|ico|webp))', r'\1/website/\2', html)
        return html


register_plugin_type("HtmlRenderPlugin", HtmlRenderPlugin)


def New():
    return HtmlRenderPlugin()
