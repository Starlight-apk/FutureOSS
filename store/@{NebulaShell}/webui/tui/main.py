"""TUI 插件 - 终端用户界面，与 WebUI 双启动"""
import os
import sys
import threading
import time
from pathlib import Path
from oss.logger.logger import Log
from oss.plugin.types import Plugin, Response, register_plugin_type

from .tui.converter import TUIManager, TUIRenderer, HTMLToTUIConverter


class TUIPlugin(Plugin):
    """TUI 插件 - 提供终端界面，通过访问 WebUI 的 /tui 接口获取 HTML"""

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
        """注入 webui 引用"""
        self.webui = webui
        
    def set_http_api(self, http_api):
        """注入 http_api 引用"""
        self.http_api = http_api

    def init(self, deps: dict = None):
        """初始化 TUI"""
        Log.info("tui", "TUI 插件初始化中...")
        
        # 创建 TUI 管理器
        self.tui_manager = TUIManager.get_instance()
        
        # 注册 /tui 路由供 TUI 访问 WebUI 页面
        if self.http_api and self.http_api.router:
            # 注册 TUI 专用 API
            self.http_api.router.get("/tui/index.html", self._handle_tui_index)
            self.http_api.router.get("/tui/page", self._handle_tui_page)
            self.http_api.router.get("/tui/css", self._handle_tui_css)
            self.http_api.router.post("/tui/interact", self._handle_tui_interact)
            Log.ok("tui", "已注册 TUI API 路由")
        else:
            Log.warn("tui", "警告：未找到 http-api 依赖")
        
        # 加载默认页面（从 WebUI 获取）
        self._load_default_pages()
        
        Log.ok("tui", "TUI 插件初始化完成")

    def _load_default_pages(self):
        """从 WebUI 加载默认页面到 TUI"""
        # 模拟访问 WebUI 页面并缓存
        default_pages = ["/", "/dashboard", "/logs", "/terminal"]
        
        for path in default_pages:
            try:
                # 这里会通过内部调用获取 WebUI 渲染的 HTML
                html = self._fetch_webui_page(path)
                if html:
                    self.tui_manager.load_page(path, html)
                    Log.info("tui", f"已加载页面：{path}")
            except Exception as e:
                Log.warn("tui", f"加载页面 {path} 失败：{e}")

    def _fetch_webui_page(self, path: str) -> str:
        """从 WebUI 获取页面 HTML"""
        if not self.webui or not hasattr(self.webui, 'server'):
            return ""
        
        # 模拟请求获取 WebUI 页面
        # 由于我们在同一进程，可以直接调用 server 的路由处理
        try:
            from oss.plugin.types import Request
            request = Request(method="GET", path=path, headers={}, body="")
            
            # 查找匹配的路由
            router = self.webui.server.router
            if hasattr(router, 'routes'):
                for route_path, handler in router.routes.items():
                    if route_path == path or (route_path.endswith('*') and path.startswith(route_path[:-1])):
                        response = handler(request)
                        if response and hasattr(response, 'body'):
                            return response.body.decode('utf-8') if isinstance(response.body, bytes) else response.body
        except Exception as e:
            Log.warn("tui", f"获取 WebUI 页面失败：{e}")
        
        return ""

    def start(self):
        """启动 TUI（在后台线程运行）"""
        Log.info("tui", "TUI 启动中...")
        self.running = True
        
        # 在后台线程运行 TUI
        self.tui_thread = threading.Thread(target=self._tui_loop, daemon=True)
        self.tui_thread.start()
        
        Log.ok("tui", "TUI 已启动（后台模式）")
        Log.info("tui", "提示：按 'q' 退出 TUI，WebUI 仍在运行")

    def _tui_loop(self):
        """TUI 主循环"""
        try:
            # 显示欢迎界面
            self._show_welcome()
            
            # 主事件循环
            self._event_loop()
            
        except Exception as e:
            Log.error("tui", f"TUI 循环异常：{e}")
        finally:
            self.running = False

    def _show_welcome(self):
        """显示欢迎界面"""
        welcome_html = """
        <!DOCTYPE html>
        <html>
        <head><title>NebulaShell TUI</title></head>
        <body>
            <h1>👋 欢迎使用 NebulaShell TUI</h1>
            <p>终端用户界面已启动</p>
            <p>WebUI 同时运行在：http://localhost:8080</p>
            <hr>
            <h2>可用命令:</h2>
            <ul>
                <li>[1] 首页</li>
                <li>[2] 仪表盘</li>
                <li>[3] 日志</li>
                <li>[4] 终端</li>
                <li>[q] 退出 TUI</li>
                <li>[r] 刷新</li>
            </ul>
        </body>
        </html>
        """
        self.tui_manager.load_page("/welcome", welcome_html)
        self._render_current("/welcome")

    def _render_current(self, path: str = None):
        """渲染当前页面到终端"""
        if path is None:
            path = self.tui_manager.current_page or "/welcome"
        
        output = self.tui_manager.render_page(path)
        
        # 清屏并输出
        sys.stdout.write('\x1b[2J\x1b[H')
        sys.stdout.write(output)
        sys.stdout.write('\n\n')
        sys.stdout.write('\x1b[90m提示：按数字键导航，q 退出\x1b[0m\n')
        sys.stdout.flush()

    def _event_loop(self):
        """简单的事件循环"""
        import sys
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            
            while self.running:
                char = sys.stdin.read(1)
                
                if char == '\x03':  # Ctrl+C
                    break
                elif char == '\x04':  # Ctrl+D
                    break
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
                elif char == 'r':
                    self._load_default_pages()
                    self._render_current()
                elif char == '\n' or char == '\r':
                    # Enter 刷新当前页
                    self._render_current()
                    
        except Exception as e:
            Log.error("tui", f"事件循环错误：{e}")
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _handle_tui_index(self, request):
        """处理 /tui/index.html 请求"""
        # 返回特殊标记的 HTML，TUI 会识别并转换
        html = """<!DOCTYPE html>
<html class="tui-page">
<head>
    <meta charset="UTF-8">
    <title>NebulaShell TUI</title>
    <!-- TUI 标记：此页面专为终端渲染 -->
</head>
<body class="tui-body">
    <div class="tui-container">
        <h1>NebulaShell TUI</h1>
        <p>终端界面就绪</p>
        <div class="tui-nav">
            <a href="/" data-tui-action="navigate">首页</a>
            <a href="/dashboard" data-tui-action="navigate">仪表盘</a>
            <a href="/logs" data-tui-action="navigate">日志</a>
            <a href="/terminal" data-tui-action="navigate">终端</a>
        </div>
    </div>
    <!-- TUI 脚本标记：这些会被转换为键盘绑定 -->
    <script type="application/x-tui-keys">
        {"1": "/", "2": "/dashboard", "3": "/logs", "4": "/terminal", "q": "quit", "r": "refresh"}
    </script>
</body>
</html>"""
        return Response(
            status=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body=html
        )

    def _handle_tui_page(self, request):
        """处理 /tui/page 请求 - 获取任意页面的 TUI 版本"""
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(request.path)
        params = parse_qs(parsed.query)
        page_path = params.get('path', ['/'])[0]
        
        # 从 WebUI 获取原始 HTML
        html = self._fetch_webui_page(page_path)
        
        if html:
            # 添加 TUI 标记
            html = html.replace('<html', '<html class="tui-page"')
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
            return Response(
                status=404,
                headers={"Content-Type": "text/html"},
                body="<html><body>Page not found</body></html>"
            )

    def _handle_tui_css(self, request):
        """处理 /tui/css 请求 - 返回终端兼容的 CSS"""
        # 只返回终端支持的 CSS 属性
        css = """/* TUI 兼容 CSS */
.tui-page {
    /* 背景色 - 仅支持 ANSI 颜色 */
    background-color: #000000;
    color: #ffffff;
}

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
"""
        return Response(
            status=200,
            headers={"Content-Type": "text/css"},
            body=css
        )

    def _handle_tui_interact(self, request):
        """处理 TUI 交互请求"""
        import json
        
        try:
            body = json.loads(request.body)
            action = body.get('action', '')
            target = body.get('target', '')
            
            # 处理交互
            if action == 'navigate':
                # 导航到指定页面
                html = self._fetch_webui_page(target)
                if html:
                    self.tui_manager.load_page(target, html)
                    return Response(
                        status=200,
                        headers={"Content-Type": "application/json"},
                        body=json.dumps({'success': True, 'page': target})
                    )
            elif action == 'click':
                # 处理点击
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True})
                )
            elif action == 'keypress':
                # 处理按键
                key = body.get('key', '')
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True, 'key': key})
                )
            
            return Response(
                status=400,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': 'Unknown action'})
            )
            
        except Exception as e:
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def stop(self):
        """停止 TUI"""
        Log.info("tui", "TUI 停止中...")
        self.running = False
        
        if self.tui_thread:
            self.tui_thread.join(timeout=2)
        
        Log.ok("tui", "TUI 已停止")


register_plugin_type("TUIPlugin", TUIPlugin)


def New():
    return TUIPlugin()
