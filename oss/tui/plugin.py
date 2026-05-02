"""TUI 插件 - 终端用户界面，与 WebUI 双启动

强大的转换层架构：
- 只访问 WebUI 开放的 /tui 接口
- 自动解析 .html 文件（入口是 index.html）
- 支持终端兼容的 CSS（背景、字体排版样式）
- 支持基础 JS 交互（鼠标位置、点击、按键）
- 参考 opencode 风格的现代化终端体验
"""
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
    """TUI 插件 - 提供终端界面，通过访问 WebUI 的 /tui 接口获取 HTML"""

    def __init__(self):
        self.webui = None
        self.http_api = None
        self.tui_manager = None
        self.running = False
        self.tui_thread = None
        self.server = None
        
    def meta(self):
        from oss.plugin.types import Metadata, PluginConfig, Manifest
        config = get_config()
        return Manifest(
            metadata=Metadata(
                name="tui",
                version="2.0.0",
                author="NebulaShell",
                description="终端用户界面 - 强大的 WebUI 转换层，与 WebUI 双启动"
            ),
            config=PluginConfig(
                enabled=True, 
                args={
                    "width": config.get("TUI_WIDTH", 80),
                    "height": config.get("TUI_HEIGHT", 24),
                    "theme": "dark",
                    "mouse_enabled": True,
                }
            ),
            dependencies=["http-api", "webui"]
        )

    def set_webui(self, webui):
        """注入 webui 引用"""
        self.webui = webui
        
    def set_http_api(self, http_api):
        """注入 http_api 引用"""
        self.http_api = http_api

    def init(self, deps: dict = None):
        """初始化 TUI - 注册 /tui 接口供转换层访问"""
        Log.info("tui", "TUI 插件初始化中...")
        
        # 创建 TUI 管理器
        config = get_config()
        width = config.get("TUI_WIDTH", 80)
        height = config.get("TUI_HEIGHT", 24)
        self.tui_manager = TUIManager.get_instance(width, height)
        
        # 注册 /tui 路由供 TUI 转换层访问 WebUI 页面
        if self.http_api and self.http_api.router:
            # 核心接口：/tui/index.html - TUI 入口
            self.http_api.router.get("/tui/index.html", self._handle_tui_index)
            # 核心接口：/tui/page - 获取任意页面的 TUI 版本
            self.http_api.router.get("/tui/page", self._handle_tui_page)
            # 核心接口：/tui/css - 返回终端兼容的 CSS
            self.http_api.router.get("/tui/css", self._handle_tui_css)
            # 核心接口：/tui/js - 返回 TUI 交互配置（模拟 JS）
            self.http_api.router.get("/tui/js", self._handle_tui_js)
            # 核心接口：/tui/interact - 处理 TUI 交互事件
            self.http_api.router.post("/tui/interact", self._handle_tui_interact)
            # 核心接口：/tui/pages - 列出所有可用页面
            self.http_api.router.get("/tui/pages", self._handle_tui_pages)
            
            Log.ok("tui", "已注册 TUI API 路由 (/tui/*)")
        else:
            Log.warn("tui", "警告：未找到 http-api 依赖")
        
        # 从 WebUI 加载默认页面到 TUI 缓存
        self._load_default_pages()
        
        Log.ok("tui", "TUI 插件初始化完成 - 强大的转换层已就绪")

    def _load_default_pages(self):
        """从 WebUI 加载默认页面到 TUI 缓存"""
        default_pages = ["/", "/dashboard", "/logs", "/terminal", "/plugins"]
        
        for path in default_pages:
            try:
                html = self._fetch_webui_page(path)
                if html:
                    self.tui_manager.load_page(path, html)
                    Log.info("tui", f"已加载页面：{path}")
            except Exception as e:
                Log.debug("tui", f"加载页面 {path} 失败：{e}")

    def _fetch_webui_page(self, path: str) -> str:
        """从 WebUI 获取页面 HTML - 转换层核心方法
        
        此方法模拟访问 WebUI 页面并获取 HTML，然后由 TUI 转换层解析。
        WebUI 开放的 /tui 接口会返回带有特殊标记的 HTML，不含用户可见内容，
        但包含 data-tui-* 属性和 script[type='application/x-tui-*'] 配置。
        """
        if not self.webui or not hasattr(self.webui, 'server'):
            return ""
        
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
            Log.debug("tui", f"获取 WebUI 页面失败：{e}")
        
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
        sys.stdout.write('\x1b[90m提示：按数字键导航，q 退出，r 刷新\x1b[0m\n')
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
                elif char == '5':
                    self._render_current("/plugins")
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

    # ========== TUI 核心接口实现 ==========
    
    def _handle_tui_index(self, request):
        """处理 /tui/index.html 请求 - TUI 入口点
        
        返回特殊标记的 HTML，TUI 转换层会识别并转换。
        此 HTML 不含用户可见内容，仅包含 data-tui-* 标记和配置脚本。
        """
        html = """<!DOCTYPE html>
<html class="tui-page" data-tui-version="2.0">
<head>
    <meta charset="UTF-8">
    <title>NebulaShell TUI</title>
    <!-- TUI 标记：此页面专为终端渲染 -->
    <style type="text/x-tui-css">
/* 终端兼容 CSS */
.tui-page { background-color: #000000; color: #ffffff; }
.tui-body { font-family: monospace; }
.bold { font-weight: bold; }
.underline { text-decoration: underline; }
.header { font-weight: bold; font-size: large; }
.panel { border-style: single; }
    </style>
</head>
<body class="tui-body">
    <div class="tui-container" data-tui-layout="vertical">
        <header data-tui-type="header">
            <h1>NebulaShell TUI</h1>
            <p>终端界面就绪</p>
        </header>
        
        <separator data-tui-char="─"/>
        
        <nav data-tui-type="nav" data-tui-layout="horizontal">
            <a href="/" data-tui-action="navigate" data-tui-key="1">首页</a>
            <a href="/dashboard" data-tui-action="navigate" data-tui-key="2">仪表盘</a>
            <a href="/logs" data-tui-action="navigate" data-tui-key="3">日志</a>
            <a href="/terminal" data-tui-action="navigate" data-tui-key="4">终端</a>
        </nav>
        
        <separator data-tui-char="─"/>
        
        <section data-tui-type="panel" data-tui-title="快捷操作">
            <button data-tui-key="r" data-tui-action="refresh">刷新 [r]</button>
            <button data-tui-key="q" data-tui-action="quit">退出 [q]</button>
        </section>
    </div>
    
    <!-- TUI 脚本标记：键盘绑定配置 -->
    <script type="application/x-tui-keys">
{"1": {"action": "navigate", "target": "/"}, "2": {"action": "navigate", "target": "/dashboard"}, "3": {"action": "navigate", "target": "/logs"}, "4": {"action": "navigate", "target": "/terminal"}, "r": {"action": "refresh"}, "q": {"action": "quit"}}
    </script>
    
    <!-- TUI 配置 -->
    <script type="application/x-tui-config">
{"display": {"width": 80, "height": 24}, "mouse": {"enabled": true}, "keyboard": {"enabled": true}}
    </script>
</body>
</html>"""
        return Response(
            status=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            body=html
        )

    def _handle_tui_page(self, request):
        """处理 /tui/page 请求 - 获取任意页面的 TUI 版本
        
        从 WebUI 获取原始 HTML，添加 TUI 标记后返回。
        TUI 转换层会自动解析这些标记并转换为终端元素。
        """
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(request.path)
        params = parse_qs(parsed.query)
        page_path = params.get('path', ['/'])[0]
        
        # 从 WebUI 获取原始 HTML
        html = self._fetch_webui_page(page_path)
        
        if html:
            # 添加 TUI 标记
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
            # 返回错误页面
            error_html = """<!DOCTYPE html>
<html class="tui-page">
<body class="tui-body">
    <h1>❌ 页面未找到</h1>
    <p>路径：<span id="path"></span></p>
    <button data-tui-key="b" data-tui-action="back">返回</button>
    <script type="application/x-tui-keys">{"b": {"action": "back"}}</script>
</body>
</html>"""
            return Response(
                status=404,
                headers={"Content-Type": "text/html; charset=utf-8"},
                body=error_html
            )

    def _handle_tui_css(self, request):
        """处理 /tui/css 请求 - 返回终端兼容的 CSS
        
        只返回终端支持的 CSS 属性：
        - 背景色（ANSI 颜色）
        - 文字颜色（ANSI 颜色）
        - 字体样式（bold, italic, underline）
        - 边框样式（单线、双线、圆角等）
        """
        css = """/* TUI 兼容 CSS - 仅支持终端属性 */

/* 基础样式 */
.tui-page {
    background-color: #000000;
    color: #ffffff;
}

.tui-body {
    font-family: monospace;
    font-weight: normal;
}

/* 字体样式 - TUI 支持 */
.bold { font-weight: bold; }
.italic { font-style: italic; }
.underline { text-decoration: underline; }
.dim { opacity: 0.7; }

/* 布局 - TUI 简化处理 */
.tui-container {
    padding: 0;
    margin: 0;
}

[data-tui-layout="vertical"] {
    display: block;
}

[data-tui-layout="horizontal"] {
    display: inline-block;
}

/* 边框样式 */
[data-tui-border="single"] {
    border-style: single;
}

[data-tui-border="double"] {
    border-style: double;
}

[data-tui-border="rounded"] {
    border-style: rounded;
}

/* 交互元素标记 */
[data-tui-action] {
    cursor: pointer;
}

[data-tui-key]::before {
    content: "[" attr(data-tui-key) "] ";
}

/* 面板/卡片 */
[data-tui-type="panel"] {
    border-style: single;
    padding: 1;
}

/* 按钮 */
button, [data-tui-type="button"] {
    border-style: single;
    padding: 0 2;
}

/* 列表 */
ul, ol {
    list-style-position: inside;
}

/* 进度条 */
[data-tui-type="progress"] {
    filled-char: "█";
    empty-char: "░";
}

/* 加载动画 */
[data-tui-type="spinner"] {
    animation: spin 1s linear infinite;
}
"""
        return Response(
            status=200,
            headers={"Content-Type": "text/css"},
            body=css
        )

    def _handle_tui_js(self, request):
        """处理 /tui/js 请求 - 返回 TUI 交互配置（模拟 JS）
        
        TUI 不支持完整 JavaScript，只支持：
        - 获取鼠标位置
        - 点击事件
        - 按键事件
        - 简单的 DOM 操作
        """
        js_config = """// TUI JS 模拟配置
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
"""
        return Response(
            status=200,
            headers={"Content-Type": "application/javascript"},
            body=js_config
        )

    def _handle_tui_interact(self, request):
        """处理 TUI 交互请求 - 处理鼠标、键盘事件"""
        import json
        
        try:
            body = json.loads(request.body)
            action = body.get('action', '')
            target = body.get('target', '')
            key = body.get('key', '')
            mouse_x = body.get('mouse_x', 0)
            mouse_y = body.get('mouse_y', 0)
            
            # 处理导航
            if action == 'navigate':
                html = self._fetch_webui_page(target)
                if html:
                    self.tui_manager.load_page(target, html)
                    return Response(
                        status=200,
                        headers={"Content-Type": "application/json"},
                        body=json.dumps({'success': True, 'page': target})
                    )
            
            # 处理点击
            elif action == 'click':
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True, 'target': target})
                )
            
            # 处理按键
            elif action == 'keypress':
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True, 'key': key})
                )
            
            # 处理鼠标移动
            elif action == 'mousemove':
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True, 'x': mouse_x, 'y': mouse_y})
                )
            
            # 处理刷新
            elif action == 'refresh':
                self._load_default_pages()
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True})
                )
            
            # 处理退出
            elif action == 'quit':
                self.running = False
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True, 'message': 'Quitting TUI'})
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

    def _handle_tui_pages(self, request):
        """处理 /tui/pages 请求 - 列出所有可用页面"""
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
        """前台阻塞等待 TUI 退出（用于 CLI 模式）"""
        if self.tui_thread and self.tui_thread.is_alive():
            self.tui_thread.join()

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
