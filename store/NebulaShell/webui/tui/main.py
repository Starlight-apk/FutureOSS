
    def __init__(self):
        self.webui = None
        self.http_api = None
        self.tui_manager = None
        self.running = False
        self.tui_thread = None
        
    def meta(self):
        from oss.plugin.types import Metadata, PluginConfig, Manifest
        return Manifest(
            metadata=Metadata(
                name="tui",
                version="1.0.0",
                author="NebulaShell",
                description="终端用户界面 - 与 WebUI 双启动"
            ),
            config=PluginConfig(enabled=True, args={}),
            dependencies=["http-api", "webui"]
        )

    def set_webui(self, webui):
        self.http_api = http_api

    def init(self, deps: dict = None):
        default_pages = ["/", "/dashboard", "/logs", "/terminal"]
        
        for path in default_pages:
            try:
                html = self._fetch_webui_page(path)
                if html:
                    self.tui_manager.load_page(path, html)
                    Log.info("tui", f"已加载页面：{path}")
            except Exception as e:
                Log.warn("tui", f"加载页面 {path} 失败：{e}")

    def _fetch_webui_page(self, path: str) -> str:
        Log.info("tui", "TUI 启动中...")
        self.running = True
        
        self.tui_thread = threading.Thread(target=self._tui_loop, daemon=True)
        self.tui_thread.start()
        
        Log.ok("tui", "TUI 已启动（后台模式）")
        Log.info("tui", "提示：按 'q' 退出 TUI，WebUI 仍在运行")

    def _tui_loop(self):
        welcome_html = 
        return Response(
            status=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body=html
        )

    def _handle_tui_page(self, request):
        css = """/* TUI 兼容 CSS */
.tui-page {
    /* 背景色 - 仅支持 ANSI 颜色 */
    background-color:    color:}

.tui-body {
    font-family: monospace;
    font-weight: normal;
}

/* 字体样式 - TUI 支持 */
.bold { font-weight: bold; }
.underline { text-decoration: underline; }

/* 布局 - TUI 简化处理 */
.tui-container {
    padding: 0;
    margin: 0;
}

/* 交互元素标记 */
[data-tui-action] {
    cursor: pointer;
}
        return Response(
            status=200,
            headers={"Content-Type": "text/css"},
            body=css
        )

    def _handle_tui_interact(self, request):
        Log.info("tui", "TUI 停止中...")
        self.running = False
        
        if self.tui_thread:
            self.tui_thread.join(timeout=2)
        
        Log.ok("tui", "TUI 已停止")


register_plugin_type("TUIPlugin", TUIPlugin)


def New():
    return TUIPlugin()
