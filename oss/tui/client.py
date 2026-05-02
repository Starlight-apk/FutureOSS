"""TUI 客户端 - 前后端分离的 TUI 前端

通过 HTTP 连接后端 nebula serve，消费 JSON API，
直接使用 ANSI 转义码绘制专业终端界面。
支持鼠标点击导航。
"""
import sys
import json
import time
import tty
import termios
import signal
import socket
import urllib.request
import urllib.error
import shutil
import re
from typing import Optional


# ── ANSI 工具 ────────────────────────────────────────────

def fg(r, g, b): return f"\x1b[38;2;{r};{g};{b}m"
def bg(r, g, b): return f"\x1b[48;2;{r};{g};{b}m"
def bold(s): return f"\x1b[1m{s}\x1b[22m"
def dim(s): return f"\x1b[2m{s}\x1b[22m"
def rst(): return "\x1b[0m"

C = {
    "header_bg": (30, 30, 46),
    "status_bg": (30, 30, 46),
    "accent":    (0, 255, 135),
    "green":     (0, 255, 135),
    "yellow":    (255, 220, 80),
    "red":       (255, 80, 80),
    "cyan":      (80, 200, 255),
    "dim":       (100, 100, 120),
    "white":     (220, 220, 240),
    "bar_bg":    (50, 50, 70),
}

# ── 鼠标转义 ────────────────────────────────────────────

_MOUSE_ON = "\x1b[?1000h\x1b[?1002h\x1b[?1006h"
_MOUSE_OFF = "\x1b[?1006l\x1b[?1002l\x1b[?1000l"

# ── HTTP 请求 ────────────────────────────────────────────

def http_get(url: str, timeout=5) -> Optional[str]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8")
    except Exception:
        return None


def backend_alive(host="127.0.0.1", port=8080) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        return True
    except OSError:
        return False


# ── 布局工具 ────────────────────────────────────────────

def term_size():
    return shutil.get_terminal_size((80, 24))


def hbar(width: int, percent: float, color_fg=(0, 255, 135), color_bg=(50, 50, 70), char="█"):
    filled = max(0, min(width, int(width * percent / 100)))
    empty = width - filled
    bar = fg(*color_fg) + char * filled + rst() + fg(*color_bg) + "░" * empty + rst()
    return bar


# ── TUI 客户端 ──────────────────────────────────────────

Page = dict  # {"id": str, "label": str, "desc": str}


class TUIClient:
    _resize_flag = False

    @classmethod
    def _sigwinch(cls, sig, frame):
        cls._resize_flag = True

    PAGES: list[Page] = [
        {"id": "welcome",   "label": "首页",     "desc": "系统概览"},
        {"id": "dashboard", "label": "仪表盘",   "desc": "CPU · 内存 · 磁盘 · 网络"},
        {"id": "logs",      "label": "日志",     "desc": "实时日志输出"},
        {"id": "terminal",  "label": "终端",     "desc": "Shell"},
        {"id": "plugins",   "label": "插件",     "desc": "插件管理"},
    ]

    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.running = False
        self.current_page = "welcome"
        self.width = 80
        self.height = 24
        self._stats_cache = {}
        self._stats_time = 0

        # 鼠标点击区域: list of (y, page_id)
        self._click_zones: list[tuple[int, str]] = []

    def _fetch_stats(self) -> dict:
        now = time.time()
        if now - self._stats_time < 1 and self._stats_cache:
            return self._stats_cache
        raw = http_get(f"{self.base_url}/api/dashboard/stats")
        if raw:
            try:
                self._stats_cache = json.loads(raw)
                self._stats_time = now
            except json.JSONDecodeError:
                pass
        return self._stats_cache

    # ── 鼠标事件 ──────────────────────────────────────────

    @staticmethod
    def _parse_sgr_mouse(data: str):
        """解析 SGR 鼠标事件 \x1b[<button;x;y;M/m → (button, x, y)"""
        m = re.match(r"^\x1b\[<(\d+);(\d+);(\d+)([Mm])$", data)
        if m:
            return int(m.group(1)), int(m.group(2)), int(m.group(3))
        return None

    # ── 屏幕渲染 ──────────────────────────────────────────

    def _draw_header(self):
        w = self.width
        alive = backend_alive(self.host, self.port)
        status_icon = "●" if alive else "○"
        status_color = C["green"] if alive else C["red"]

        print(bg(*C["header_bg"]), end="")
        print(" " * w, end="")
        print(f"\r{bg(*C['header_bg'])} ", end="")

        title = " NebulaShell TUI "
        print(fg(*C["accent"]) + bold(title) + rst(), end="")
        print(bg(*C["header_bg"]), end="")

        right = f" {fg(*status_color)}{status_icon}{rst()}{bg(*C['header_bg'])} {fg(*C['dim'])}{self.host}:{self.port}{rst()}"
        print(f"\x1b[{w - len(right) + 1}G{right}", end="")
        print(rst())

    def _draw_status_bar(self):
        w = self.width
        print(bg(*C["status_bg"]), end="")
        print(" " * w, end="")
        print(f"\r{bg(*C['status_bg'])} ", end="")

        nav_hint = f"{fg(*C['dim'])}数字/点击导航  q 退出  r 刷新{rst()}"
        page_name = self.current_page.upper()
        page_info = f"{fg(*C['cyan'])}{page_name}{rst()}"
        print(f"\r{bg(*C['status_bg'])} {page_info}", end="")
        print(f"\x1b[{w - len(nav_hint) + 1}G{nav_hint}", end="")
        print(rst())

    def _clear(self):
        print("\x1b[2J\x1b[H", end="")

    def _render_all(self):
        self._click_zones.clear()
        self._clear()
        self._draw_header()
        print()
        content_top = 2  # header(1) + blank(1) = 2

        alive = backend_alive(self.host, self.port)
        if self.current_page == "welcome":
            self._render_welcome(alive, content_top)
        elif self.current_page == "dashboard":
            self._render_dashboard()
        elif self.current_page == "logs":
            self._render_logs()
        elif self.current_page == "terminal":
            self._render_terminal()
        elif self.current_page == "plugins":
            self._render_plugins()
        else:
            self._render_home()

        used = self._content_lines + 4
        for _ in range(self.height - used):
            print()
        self._draw_status_bar()
        sys.stdout.flush()

    # ── 页面内容 ──────────────────────────────────────────

    def _render_welcome(self, alive: bool, top: int):
        w = self.width
        self._content_lines = 0

        logo = [
            "███╗   ██╗███████╗██████╗ ██╗   ██╗██╗      █████╗ ",
            "████╗  ██║██╔════╝██╔══██╗██║   ██║██║     ██╔══██╗",
            "██╔██╗ ██║█████╗  ██████╔╝██║   ██║██║     ███████║",
            "██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║██║     ██╔══██║",
            "██║ ╚████║███████╗██████╔╝╚██████╔╝███████╗██║  ██║",
            "╚═╝  ╚═══╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝",
        ]
        for line in logo:
            print("  " + fg(*C["accent"]) + line + rst())
            self._content_lines += 1

        print()
        self._content_lines += 1

        print(f"  {fg(*C['dim'])}一切皆为插件的开发者工具运行时框架{rst()}")
        self._content_lines += 1
        print()
        self._content_lines += 1

        if alive:
            print(f"  {fg(*C['green'])}● 后端已连接{rst()}  {fg(*C['dim'])}{self.base_url}{rst()}")
        else:
            print(f"  {fg(*C['red'])}○ 后端未连接{rst()}  {fg(*C['dim'])}{self.base_url}{rst()}")
            self._content_lines += 1
            print(f"  {fg(*C['dim'])}请先启动后端: nebula serve{rst()}")
        self._content_lines += 1

        print()
        self._content_lines += 1

        print(f"  {fg(*C['dim'])}─ 点击或按键导航 ─{rst()}")
        self._content_lines += 1

        for i, pg in enumerate(self.PAGES):
            line_y = top + self._content_lines
            self._click_zones.append((line_y, pg["id"]))
            key = str(i + 1) if i < 9 else "0"
            print(f"  [{fg(*C['accent'])}{key}{rst()}]  {bold(pg['label'])}  {fg(*C['dim'])}{pg['desc']}{rst()}")
            self._content_lines += 1

    def _render_home(self):
        w = self.width
        self._content_lines = 0
        stats = self._fetch_stats()
        if not stats:
            print(f"  {fg(*C['dim'])}无法获取系统信息{rst()}")
            self._content_lines += 1
            return

        uptime = stats.get("uptime", "N/A")
        processes = stats.get("processes", 0)
        cpu = stats.get("cpu", {})
        mem = stats.get("ram", {})
        disk = stats.get("disk", {})

        print(f"  {bold('系统概览')}")
        self._content_lines += 1
        print(f"  {fg(*C['dim'])}运行时间: {uptime}    进程数: {processes}{rst()}")
        self._content_lines += 1
        print()
        self._content_lines += 1

        bar_w = w - 30

        cpu_p = cpu.get("percent", 0)
        print(f"  CPU    {fg(*C['dim'])}{str(cpu_p).rjust(5)}%{rst()}  {hbar(bar_w, cpu_p, C['green'] if cpu_p < 50 else C['yellow'] if cpu_p < 80 else C['red'])}")
        self._content_lines += 1

        ram_p = mem.get("percent", 0)
        ram_u = mem.get("used", 0)
        ram_t = mem.get("total", 0)
        print(f"  内存   {fg(*C['dim'])}{str(ram_p).rjust(5)}%{rst()}  {hbar(bar_w, ram_p, C['green'] if ram_p < 50 else C['yellow'] if ram_p < 80 else C['red'])}  {fg(*C['dim'])}{ram_u}G / {ram_t}G{rst()}")
        self._content_lines += 1

        disk_p = disk.get("percent", 0)
        disk_u = disk.get("used", 0)
        disk_t = disk.get("total", 0)
        print(f"  磁盘   {fg(*C['dim'])}{str(disk_p).rjust(5)}%{rst()}  {hbar(bar_w, disk_p, C['green'] if disk_p < 50 else C['yellow'] if disk_p < 80 else C['red'])}  {fg(*C['dim'])}{disk_u}G / {disk_t}G{rst()}")
        self._content_lines += 1

        net = stats.get("network", {})
        recv = net.get("recv_rate", 0)
        sent = net.get("sent_rate", 0)
        latency = stats.get("latency", 0)
        print(f"  网络   {fg(*C['dim'])}▼ {self._fmt_bytes(recv)}/s  ▲ {self._fmt_bytes(sent)}/s  延迟: {latency}ms{rst()}")
        self._content_lines += 1

        load = stats.get("load", {})
        l1 = load.get("load1", 0)
        l5 = load.get("load5", 0)
        l15 = load.get("load15", 0)
        print(f"  负载   {fg(*C['dim'])}1m: {l1}  5m: {l5}  15m: {l15}{rst()}")
        self._content_lines += 1

    def _render_dashboard(self):
        w = self.width
        self._content_lines = 0
        stats = self._fetch_stats()
        if not stats:
            print(f"  {fg(*C['dim'])}无法获取仪表盘数据{rst()}")
            self._content_lines += 1
            return

        print(f"  {bold('系统仪表盘')}  实时监控")
        self._content_lines += 1

        cpu = stats.get("cpu", {})
        mem = stats.get("ram", {})
        disk = stats.get("disk", {})
        net = stats.get("network", {})
        disk_io = stats.get("disk_io", {})
        load = stats.get("load", {})
        latency = stats.get("latency", 0)
        processes = stats.get("processes", 0)
        uptime = stats.get("uptime", "N/A")

        bar_w = w - 36

        print()
        self._content_lines += 1

        cpu_p = cpu.get("percent", 0)
        cpu_cores = cpu.get("cores", 0)
        print(f"  {fg(*C['cyan'])}CPU     {rst()}{hbar(bar_w, cpu_p, C['green'] if cpu_p < 50 else C['yellow'] if cpu_p < 80 else C['red'])}  {fg(*C['white'])}{cpu_p}%{rst()}  {fg(*C['dim'])}({cpu_cores} 核){rst()}")
        self._content_lines += 1

        ram_p = mem.get("percent", 0)
        ram_u = mem.get("used", 0)
        ram_t = mem.get("total", 0)
        print(f"  {fg(*C['cyan'])}内存   {rst()}{hbar(bar_w, ram_p, C['green'] if ram_p < 50 else C['yellow'] if ram_p < 80 else C['red'])}  {fg(*C['white'])}{ram_p}%{rst()}  {fg(*C['dim'])}{ram_u}G / {ram_t}G{rst()}")
        self._content_lines += 1

        disk_p = disk.get("percent", 0)
        disk_u = disk.get("used", 0)
        disk_t = disk.get("total", 0)
        print(f"  {fg(*C['cyan'])}磁盘   {rst()}{hbar(bar_w, disk_p, C['green'] if disk_p < 50 else C['yellow'] if disk_p < 80 else C['red'])}  {fg(*C['white'])}{disk_p}%{rst()}  {fg(*C['dim'])}{disk_u}G / {disk_t}G{rst()}")
        self._content_lines += 1

        print()
        self._content_lines += 1

        recv = net.get("recv_rate", 0)
        sent = net.get("sent_rate", 0)
        tr = net.get("total_recv", 0)
        ts = net.get("total_sent", 0)
        print(f"  {fg(*C['cyan'])}网络   {rst()}▼ {fg(*C['green'])}{self._fmt_bytes(recv)}/s{rst()}  ▲ {fg(*C['yellow'])}{self._fmt_bytes(sent)}/s{rst()}  {fg(*C['dim'])}总量: {self._fmt_bytes(tr)} / {self._fmt_bytes(ts)}{rst()}")
        self._content_lines += 1

        disk_r = disk_io.get("read_rate", 0)
        disk_w = disk_io.get("write_rate", 0)
        print(f"  {fg(*C['cyan'])}磁盘IO {rst()}▼ {fg(*C['green'])}{self._fmt_bytes(disk_r)}/s{rst()}  ▲ {fg(*C['yellow'])}{self._fmt_bytes(disk_w)}/s{rst()}")
        self._content_lines += 1

        print()
        self._content_lines += 1

        l1 = load.get("load1", 0)
        l5 = load.get("load5", 0)
        l15 = load.get("load15", 0)
        print(f"  {fg(*C['cyan'])}负载   {rst()}1m: {fg(*C['white'])}{l1}{rst()}  5m: {fg(*C['white'])}{l5}{rst()}  15m: {fg(*C['white'])}{l15}{rst()}  进程: {fg(*C['white'])}{processes}{rst()}  延迟: {fg(*C['white'])}{latency}ms{rst()}")
        self._content_lines += 1

        print(f"  {fg(*C['cyan'])}运行   {rst()}{fg(*C['dim'])}{uptime}{rst()}")
        self._content_lines += 1

    def _render_logs(self):
        self._content_lines = 0
        print(f"  {bold('系统日志')}")
        self._content_lines += 1
        print(f"  {fg(*C['dim'])}实时日志输出（待实现）{rst()}")
        self._content_lines += 1

    def _render_terminal(self):
        self._content_lines = 0
        print(f"  {bold('终端')}")
        self._content_lines += 1
        print(f"  {fg(*C['dim'])}Shell 终端（待实现）{rst()}")
        self._content_lines += 1

    def _render_plugins(self):
        self._content_lines = 0
        print(f"  {bold('插件管理')}")
        self._content_lines += 1
        print(f"  {fg(*C['dim'])}插件列表（待实现）{rst()}")
        self._content_lines += 1

    # ── 工具 ──────────────────────────────────────────────

    @staticmethod
    def _fmt_bytes(b):
        if b > 1024**3:
            return f"{b/(1024**3):.1f}G"
        if b > 1024**2:
            return f"{b/(1024**2):.1f}M"
        if b > 1024:
            return f"{b/1024:.1f}K"
        return f"{b:.0f}B"

    # ── 主循环 ────────────────────────────────────────────

    def _navigate(self, page_id: str):
        self._stats_cache = {}
        self._stats_time = 0
        self.current_page = page_id
        self.width, self.height = term_size()
        self._render_all()

    def run(self):
        self.width, self.height = term_size()
        self.running = True
        self._render_all()

        signal.signal(signal.SIGWINCH, TUIClient._sigwinch)

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            # setraw 会关闭 ONLCR（\n→\r\n），重新开启避免阶梯乱码
            attrs = termios.tcgetattr(fd)
            attrs[1] = attrs[1] | termios.ONLCR
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
            sys.stdout.write(_MOUSE_ON)
            sys.stdout.flush()

            buf = ""
            while self.running:
                # 终端 resize 检测
                if TUIClient._resize_flag:
                    TUIClient._resize_flag = False
                    self.width, self.height = term_size()
                    self._render_all()

                ch = sys.stdin.read(1)
                buf += ch

                # 检测 SGR 鼠标事件结束符 M/m
                if buf.startswith("\x1b[<") and ch in ("M", "m"):
                    ev = self._parse_sgr_mouse(buf)
                    buf = ""
                    if ev:
                        button, mx, my = ev
                        if button == 0 and ch == "M":  # 左键按下
                            for zy, page_id in self._click_zones:
                                if my == zy + 1:      # 鼠标坐标 1-based
                                    self._navigate(page_id)
                                    break
                    continue

                # 非鼠标序列 → 重置缓冲区
                if not buf.startswith("\x1b"):
                    pass
                elif buf.startswith("\x1b[<"):
                    continue  # 等待更多字符
                elif len(buf) > 1:
                    buf = ""  # 其他转义序列，丢弃

                # 处理单字符输入
                if len(buf) == 1:
                    c = buf
                    buf = ""
                    if c in ("q", "Q", "\x03", "\x04"):
                        break
                    elif c == "1":
                        self._navigate("welcome")
                    elif c == "2":
                        self._navigate("dashboard")
                    elif c == "3":
                        self._navigate("logs")
                    elif c == "4":
                        self._navigate("terminal")
                    elif c == "5":
                        self._navigate("plugins")
                    elif c in ("r", "R"):
                        self._stats_cache = {}
                        self._stats_time = 0
                        self._render_all()
        except Exception:
            pass
        finally:
            signal.signal(signal.SIGWINCH, signal.SIG_DFL)
            sys.stdout.write(_MOUSE_OFF)
            sys.stdout.flush()
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
            print("\x1b[2J\x1b[H\x1b[0mTUI 已退出\n")
