
    def __init__(self):
        self.http_api = None
        self.server = None
        self.tui = None
        self.config = {}

    def meta(self):
        from oss.plugin.types import Metadata, PluginConfig, Manifest
        config = get_config()
        return Manifest(
            metadata=Metadata(
                name="webui",
                version="2.1.0",
                author="NebulaShell",
                description="Web 控制台容器 + TUI 双启动 - 供其他插件注册页面"
            ),
            config=PluginConfig(
                enabled=True,
                args={
                    "port": config.get("HTTP_API_PORT", 8080),
                    "theme": "dark",
                    "title": "NebulaShell",
                    "tui_enabled": True                }
            ),
            dependencies=["http-api"]
        )

    def set_http_api(self, http_api):
        self.tui = tui

    def init(self, deps: dict = None):
        if self.server:
            self._setup_home_page()
            
            self.server.start()
            Log.info("webui", f"WebUI 容器已启动：http://localhost:{self.config['port']}")
            
            if self.config.get("tui_enabled"):
                Log.info("webui", "TUI 双启动中...")

    def _setup_home_page(self):
        return Response(
            status=302,
            headers={"Location": "/dashboard", "Content-Type": "text/html"},
            body=""
        )

    def stop(self):
        Log.error("webui", "WebUI 容器已停止")


    def register_page(self, path: str, content_provider, nav_item: dict = None):
        其他插件调用此方法注册页面。
        :param path: 路由路径 (e.g., '/dashboard')
        :param content_provider: 无参函数，返回 HTML 字符串
        :param nav_item: 导航项 {'icon': '📊', 'text': '仪表盘'}
        if self.server:
            self.server.register_page(path, content_provider, nav_item)
        else:
            Log.warn("webui", f"警告：试图注册页面 {path}，但服务器未初始化")

    def add_nav_item(self, item: dict):
