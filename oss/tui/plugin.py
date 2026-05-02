import os
import sys
import threading
import time
from pathlib import Path
from oss.logger.logger import Log
from oss.plugin.types import Plugin, Response, register_plugin_type
from oss.config import get_config

from oss.tui.converter import TUIManager, TUIRenderer, HTMLToTUIConverter


class TUIPlugin(Plugin):
        self.webui = webui
        
    def set_http_api(self, http_api):
        Log.info("tui", "TUI 插件初始化中...")
        
        config = get_config()
        width = config.get("TUI_WIDTH", 80)
        height = config.get("TUI_HEIGHT", 24)
        self.tui_manager = TUIManager.get_instance(width, height)
        
        if self.http_api and self.http_api.router:
            self.http_api.router.get("/tui/index.html", self._handle_tui_index)
            self.http_api.router.get("/tui/page", self._handle_tui_page)
            self.http_api.router.get("/tui/css", self._handle_tui_css)
            self.http_api.router.get("/tui/js", self._handle_tui_js)
            self.http_api.router.post("/tui/interact", self._handle_tui_interact)
            self.http_api.router.get("/tui/pages", self._handle_tui_pages)
            
            Log.ok("tui", "已注册 TUI API 路由 (/tui/*)")
        else:
            Log.warn("tui", "警告：未找到 http-api 依赖")
        
        self._load_default_pages()
        
        Log.ok("tui", "TUI 插件初始化完成 - 强大的转换层已就绪")

    def _load_default_pages(self):
        
        此方法模拟访问 WebUI 页面并获取 HTML，然后由 TUI 转换层解析。
        WebUI 开放的 /tui 接口会返回带有特殊标记的 HTML，不含用户可见内容，
        但包含 data-tui-* 属性和 script[type='application/x-tui-*'] 配置。
        if not self.webui or not hasattr(self.webui, 'server'):
            return ""
        
        try:
            from oss.plugin.types import Request
            request = Request(method="GET", path=path, headers={}, body="")
            
            router = self.webui.server.router
            if hasattr(router, 'routes'):
                for route_path, handler in router.routes.items():
                    if route_path == path or (route_path.endswith('*') and path.startswith(route_path[:-1])):
                        response = handler(request)
                        if response and hasattr(response, 'body'):
                            return response.body.decode('utf-8') if isinstance(response.body, bytes) else response.body
        except Exception as e:
            Log.debug("tui", f"获取 WebUI 页面失败：{e}")
        
        return ""

    def start(self):
        try:
            self._show_welcome()
            
            self._event_loop()
            
        except Exception as e:
            Log.error("tui", f"TUI 循环异常：{e}")
        finally:
            self.running = False

    def _show_welcome(self):
<!DOCTYPE html>
<html class="tui-page">
<head>
    <title>NebulaShell TUI</title>
    <meta charset="UTF-8">
    <!-- TUI 标记：此页面专为终端渲染 -->
</head>
<body class="tui-body">
    <header data-tui-type="header">
        <h1>👋 欢迎使用 NebulaShell TUI</h1>
        <p>终端用户界面已启动</p>
        <p>WebUI 同时运行在：http://localhost:8080</p>
    </header>
    
    <separator data-tui-char="─"/>
    
    <section data-tui-type="panel" data-tui-title="可用命令">
        <ul>
            <li>[1] 首页</li>
            <li>[2] 仪表盘</li>
            <li>[3] 日志</li>
            <li>[4] 终端</li>
            <li>[5] 插件管理</li>
            <li>[q] 退出 TUI</li>
            <li>[r] 刷新</li>
        </ul>
    </section>
    
    <separator data-tui-char="─"/>
    
    <nav data-tui-type="nav">
        <a href="/" data-tui-action="navigate" data-tui-key="1">首页</a>
        <a href="/dashboard" data-tui-action="navigate" data-tui-key="2">仪表盘</a>
        <a href="/logs" data-tui-action="navigate" data-tui-key="3">日志</a>
        <a href="/terminal" data-tui-action="navigate" data-tui-key="4">终端</a>
        <a href="/plugins" data-tui-action="navigate" data-tui-key="5">插件</a>
    </nav>
    
    <!-- TUI 脚本标记：键盘绑定配置 -->
    <script type="application/x-tui-keys">
{"1": {"action": "navigate", "target": "/"}, "2": {"action": "navigate", "target": "/dashboard"}, "3": {"action": "navigate", "target": "/logs"}, "4": {"action": "navigate", "target": "/terminal"}, "5": {"action": "navigate", "target": "/plugins"}, "q": {"action": "quit"}, "r": {"action": "refresh"}}
    </script>
</body>
</html>
        self.tui_manager.load_page("/welcome", welcome_html)
        self._render_current("/welcome")

    def _render_current(self, path: str = None):
        import sys
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            
            while self.running:
                char = sys.stdin.read(1)
                
                if char == '\x03':                    break
                elif char == '\x04':                    break
                elif char == 'q':
                    Log.info("tui", "用户退出 TUI")
                    break
                elif char == '1':
                    self._render_current("/")
                elif char == '2':
                    self._render_current("/dashboard")
                elif char == '3':
                    self._render_current("/logs")
                elif char == '4':
                    self._render_current("/terminal")
                elif char == '5':
                    self._render_current("/plugins")
                elif char == 'r':
                    self._load_default_pages()
                    self._render_current()
                elif char == '\n' or char == '\r':
                    self._render_current()
                    
        except Exception as e:
            Log.error("tui", f"事件循环错误：{e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    
    def _handle_tui_index(self, request):
        html = 
        return Response(
            status=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body=html
        )

    def _handle_tui_page(self, request):
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(request.path)
        params = parse_qs(parsed.query)
        page_path = params.get('path', ['/'])[0]
        
        html = self._fetch_webui_page(page_path)
        
        if html:
            html = html.replace('<html', '<html class="tui-page" data-tui-source="webui"')
            if '<body' in html:
                html = html.replace('<body', '<body class="tui-body"')
            else:
                html = html.replace('</head>', '<body class="tui-body"></head>')
            
            return Response(
                status=200,
                headers={"Content-Type": "text/html; charset=utf-8"},
                body=html
            )
        else:
            error_html = 
            return Response(
                status=404,
                headers={"Content-Type": "text/html; charset=utf-8"},
                body=error_html
            )

    def _handle_tui_css(self, request):
        css = // TUI JS 模拟配置
// 仅支持基础交互功能

const TUI = {
    // 鼠标支持
    mouse: {
        enabled: true,
        getPosition: () => ({ x: 0, y: 0 }),
        onClick: (handler) => {},
    },
    
    // 键盘支持
    keyboard: {
        enabled: true,
        onKeyPress: (handler) => {},
        bindings: {},
    },
    
    // DOM 操作（简化版）
    querySelector: (selector) => null,
    querySelectorAll: (selector) => [],
    
    // 事件系统
    addEventListener: (event, handler) => {},
    removeEventListener: (event, handler) => {},
};

// 导出配置
export default TUI;
        return Response(
            status=200,
            headers={"Content-Type": "application/javascript"},
            body=js_config
        )

    def _handle_tui_interact(self, request):
        import json
        
        pages = []
        if self.webui and hasattr(self.webui, 'server'):
            router = self.webui.server.router
            if hasattr(router, 'routes'):
                pages = list(router.routes.keys())
        
        return Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps({
                'success': True,
                'pages': pages,
                'current': self.tui_manager.current_page if self.tui_manager else None
            })
        )

    def wait_for_exit(self):
        Log.info("tui", "TUI 停止中...")
        self.running = False
        
        if self.tui_thread:
            self.tui_thread.join(timeout=2)
        
        Log.ok("tui", "TUI 已停止")


register_plugin_type("TUIPlugin", TUIPlugin)


def New():
    return TUIPlugin()
