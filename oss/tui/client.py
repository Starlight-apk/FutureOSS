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


_MOUSE_ON = "\x1b[?1000h\x1b[?1002h\x1b[?1006h"
_MOUSE_OFF = "\x1b[?1006l\x1b[?1002l\x1b[?1000l"


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



def term_size():
    return shutil.get_terminal_size((80, 24))


def hbar(width: int, percent: float, color_fg=(0, 255, 135), color_bg=(50, 50, 70), char="█"):
    filled = max(0, min(width, int(width * percent / 100)))
    empty = width - filled
    bar = fg(*color_fg) + char * filled + rst() + fg(*color_bg) + "░" * empty + rst()
    return bar



Page = dict

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


    @staticmethod
    def _parse_sgr_mouse(data: str):
