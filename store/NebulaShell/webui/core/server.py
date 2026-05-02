
    def __init__(self, router, config: dict):
        self.router = router
        self.config = config
        self.frontend_dir = Path(__file__).parent.parent / "frontend"
        
        self.pages = {}        self.nav_items = []
    def start(self):
        self.pages[path] = content_provider
        if nav_item:
            nav_item['url'] = path
            self.nav_items.append(nav_item)
        
        self.router.get(path, lambda req: self._render_page(path, req))

    def _render_page(self, path: str, request):
                <a href="{url}" class="nav-item {is_active}" title="{title}">
                    <i class="{ri_icon}"></i>
                </a>

        page_title = self.config.get("title", "NebulaShell")
        
        template_file = self.frontend_dir / "views" / "layout.html"
        with open(template_file, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        html = html_template.replace('{{ pageTitle }}', page_title)
        html = html.replace('{{ navItems }}', nav_html)
        html = html.replace('{{ content }}', content)
        
        return Response(
            status=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body=html
        )
    def _default_home_content(self) -> str:
        <div class="home-content">
            <div class="welcome-banner">
                <h2>👋 欢迎使用 NebulaShell</h2>
                <p>一切皆为插件的轻量级框架</p>
            </div>
        </div>

    def _execute_php(self, php_file: str, variables: dict = None) -> str:
        items = []
        for key, value in py_dict.items():
            if isinstance(value, str):
                items.append(f"'{key}' => '{value.replace(chr(39), chr(92) + chr(39))}'")
            elif isinstance(value, dict):
                items.append(f"'{key}' => {self._php_array(value)}")
            else:
                items.append(f"'{key}' => {value}")
        return "[" + ", ".join(items) + "]"

    def _php_array_list(self, py_list: list) -> str:
        
        返回特殊标记的 HTML，TUI 转换层会识别并转换。
        此 HTML 不含用户可见内容，仅包含 data-tui-* 标记和配置脚本。
        html = 
        return Response(status=200, headers={"Content-Type": "text/html; charset=utf-8"}, body=html)

    def _handle_tui_page(self, request):
<html class="tui-page" data-tui-source="webui">
<body class="tui-body">{content}</body>
</html>"""
            return Response(status=200, headers={"Content-Type": "text/html; charset=utf-8"}, body=html)
        
        return Response(status=404, headers={"Content-Type": "text/html"}, body="<html><body>Page not found</body></html>")

    def _handle_tui_css(self, request):
.tui-page { background-color:.tui-body { font-family: monospace; }
.bold { font-weight: bold; }
.underline { text-decoration: underline; }
[data-tui-action] { cursor: pointer; }
        return Response(status=200, headers={"Content-Type": "text/css"}, body=css)

    def _handle_tui_pages(self, request):
