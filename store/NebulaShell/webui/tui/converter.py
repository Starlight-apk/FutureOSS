import re
import json
import html
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
import sys


class TUIElementType(Enum):
    RESET = '\x1b[0m'
    BOLD = '\x1b[1m'
    DIM = '\x1b[2m'
    ITALIC = '\x1b[3m'
    UNDERLINE = '\x1b[4m'
    BLINK = '\x1b[5m'
    REVERSE = '\x1b[7m'
    HIDDEN = '\x1b[8m'
    
    FG_BLACK = '\x1b[30m'
    FG_RED = '\x1b[31m'
    FG_GREEN = '\x1b[32m'
    FG_YELLOW = '\x1b[33m'
    FG_BLUE = '\x1b[34m'
    FG_MAGENTA = '\x1b[35m'
    FG_CYAN = '\x1b[36m'
    FG_WHITE = '\x1b[37m'
    FG_DEFAULT = '\x1b[39m'
    
    BG_BLACK = '\x1b[40m'
    BG_RED = '\x1b[41m'
    BG_GREEN = '\x1b[42m'
    BG_YELLOW = '\x1b[43m'
    BG_BLUE = '\x1b[44m'
    BG_MAGENTA = '\x1b[45m'
    BG_CYAN = '\x1b[46m'
    BG_WHITE = '\x1b[47m'
    BG_DEFAULT = '\x1b[49m'
    
    @staticmethod
    def fg_256(color: int) -> str:
        return f'\x1b[38;5;{color}m'
    
    @staticmethod
    def bg_256(color: int) -> str:
        return f'\x1b[48;5;{color}m'


class BorderStyle:
    fg_color: str = ""
    bg_color: str = ""
    bold: bool = False
    dim: bool = False
    underline: bool = False
    italic: bool = False
    reverse: bool = False
    
    def apply(self, text: str) -> str:
    id: str = ""
    element_type: TUIElementType = TUIElementType.CONTAINER
    classes: List[str] = field(default_factory=list)
    text: str = ""
    x: int = 0
    y: int = 0
    width: int = 80
    height: int = 1
    style: TUIStyle = field(default_factory=TUIStyle)
    children: List['TUIElement'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['TUIElement'] = None
    
    def render(self) -> str:
        return (self.x, self.y, self.width, self.height)


@dataclass
class TUIButton(TUIElement):
    alignment: str = "left"    
    def render(self) -> str:
        text = self.style.apply(self.text)
        
        if self.alignment == "center":
            padding = (self.width - len(self.text)) // 2
            text = " " * padding + text
        elif self.alignment == "right":
            padding = self.width - len(self.text)
            text = " " * padding + text
        
        remaining = self.width - len(self.text)
        if remaining > 0 and self.alignment == "left":
            text += " " * remaining
        
        return text


@dataclass
class TUIPanel(TUIElement):
    layout_type: str = "vertical"    gap: int = 1
    
    def render(self, width: int = 80, height: int = 24) -> str:
        if self.layout_type == "vertical":
            rendered = []
            for i, child in enumerate(self.children):
                child.y = self.y + sum(len(r.render().split('\n')) for r in rendered) + (i * self.gap)
                rendered.append(child)
            return "\n".join(el.render() for el in rendered)
        
        elif self.layout_type == "horizontal":
            rendered = []
            current_x = self.x
            for child in self.children:
                child.x = current_x
                rendered.append(child)
                current_x += child.width + self.gap
            return "  ".join(el.render() for el in rendered)
        
        else:
            return "\n".join(el.render() for el in self.children)


@dataclass
class TUIList(TUIElement):
    char: str = "─"
    
    def render(self) -> str:
        return self.char * self.width


@dataclass
class TUIProgressBar(TUIElement):
    frames: List[str] = field(default_factory=lambda: ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    current_frame: int = 0
    
    def render(self) -> str:
        frame = self.frames[self.current_frame % len(self.frames)]
        return f"{frame} {self.text}"
    
    def next_frame(self):
        self.current_frame += 1


class HTMLToTUIConverter:
    
    COLOR_MAP = {
        '        '        '        '        '        '        '        '        '        '        'black': ANSIStyle.FG_BLACK,
        'blue': ANSIStyle.FG_BLUE,
        'green': ANSIStyle.FG_GREEN,
        'cyan': ANSIStyle.FG_CYAN,
        'red': ANSIStyle.FG_RED,
        'magenta': ANSIStyle.FG_MAGENTA,
        'yellow': ANSIStyle.FG_YELLOW,
        'white': ANSIStyle.FG_WHITE,
        'gray': ANSIStyle.DIM,
        'grey': ANSIStyle.DIM,
    }
    
    BG_COLOR_MAP = {
        '        '        '        '        '        '        '        '        'black': ANSIStyle.BG_BLACK,
        'blue': ANSIStyle.BG_BLUE,
        'green': ANSIStyle.BG_GREEN,
        'cyan': ANSIStyle.BG_CYAN,
        'red': ANSIStyle.BG_RED,
        'magenta': ANSIStyle.BG_MAGENTA,
        'yellow': ANSIStyle.BG_YELLOW,
        'white': ANSIStyle.BG_WHITE,
    }
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.keyboard_bindings: Dict[str, Dict] = {}
        self.mouse_handlers: Dict[str, Callable] = {}
        self.css_styles: Dict[str, TUIStyle] = {}
        
    def parse(self, html_content: str) -> TUILayout:
        for match in re.finditer(r'<script[^>]*type=["\']application/x-tui-config["\'][^>]*>(.*?)</script>', html, re.DOTALL):
            try:
                config = json.loads(match.group(1).strip())
                if 'keyboard' in config:
                    self.keyboard_bindings = config['keyboard']
            except json.JSONDecodeError:
                pass
        return html
    
    def _parse_tui_config(self, html: str):
        for match in re.finditer(r'<style[^>]*type=["\']text/x-tui-css["\'][^>]*>(.*?)</style>', html, re.DOTALL):
            css = match.group(1)
            for rule_match in re.finditer(r'([.                selector = rule_match.group(1)
                properties = rule_match.group(2)
                style = self._parse_css_properties(properties)
                self.css_styles[selector] = style
    
    def _parse_css_properties(self, css_text: str) -> TUIStyle:
        elements = []
        
        for match in re.finditer(r'<(\w+)([^>]*)>(.*?)</\1>', html, re.DOTALL):
            tag = match.group(1)
            attrs_str = match.group(2)
            content = match.group(3)
            
            attrs = self._parse_attributes(attrs_str)
            
            if 'data-tui-type' in attrs or self._is_tui_element(tag, attrs):
                element = self._create_tui_element(tag, attrs, content)
                if element:
                    elements.append(element)
        
        for match in re.finditer(r'<(\w+)([^/]*)/>', html):
            tag = match.group(1)
            attrs_str = match.group(2)
            attrs = self._parse_attributes(attrs_str)
            
            if 'data-tui-type' in attrs or self._is_tui_element(tag, attrs):
                element = self._create_tui_element(tag, attrs, "")
                if element:
                    elements.append(element)
        
        return elements
    
    def _parse_attributes(self, attrs_str: str) -> Dict[str, Any]:
        tui_tags = ['header', 'footer', 'nav', 'section', 'article', 'aside', 'main']
        tui_attrs = ['data-tui-type', 'data-tui-action', 'data-tui-key', 'data-tui-layout']
        
        return tag in tui_tags or any(attr in attrs for attr in tui_attrs)
    
    def _create_tui_element(self, tag: str, attrs: Dict, content: str) -> Optional[TUIElement]:
        style = TUIStyle()
        
        classes = attrs.get('class', '').split()
        for cls in classes:
            selector = f".{cls}"
            if selector in self.css_styles:
                base_style = self.css_styles[selector]
                style.fg_color = base_style.fg_color or style.fg_color
                style.bg_color = base_style.bg_color or style.bg_color
                style.bold = style.bold or base_style.bold
                style.dim = style.dim or base_style.dim
                style.underline = style.underline or base_style.underline
        
        tui_style = attrs.get('data-tui-style', '')
        if 'bold' in tui_style:
            style.bold = True
        if 'dim' in tui_style:
            style.dim = True
        if 'underline' in tui_style:
            style.underline = True
        if 'reverse' in tui_style:
            style.reverse = True
        
        return style
    
    def _extract_nav(self, html: str) -> List[TUIElement]:
        elements = []
        
        for match in re.finditer(r'<button[^>]*>(.*?)</button>', html, re.DOTALL | re.IGNORECASE):
            attrs_str = match.group(0)
            text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            text = html.unescape(text)
            
            onclick = ""
            onclick_match = re.search(r'onclick=["\']([^"\']*)["\']', attrs_str)
            if onclick_match:
                onclick = onclick_match.group(1)
            
            btn = TUIButton(
                text=text or "Button",
                action=onclick,
                width=self.width
            )
            elements.append(btn)
        
        return elements
    
    def get_keyboard_bindings(self) -> Dict[str, Dict]:
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.converter = HTMLToTUIConverter(width, height)
        self.screen_buffer: List[List[str]] = []
        
    def render(self, html: str) -> str:
        self._init_buffer()
        self._render_element(layout, 0, 0)
        return self._buffer_to_string()
    
    def _init_buffer(self):
        rendered = element.render()
        lines = rendered.split('\n')
        
        for i, line in enumerate(lines):
            if y + i >= self.height:
                break
            
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            
            for j, char in enumerate(line):
                if x + j >= self.width:
                    break
                self.screen_buffer[y + i][x + j] = char
    
    def _buffer_to_string(self) -> str:
        content = self.render(html)
        lines = content.split('\n')
        
        max_content_width = max(len(re.sub(r'\x1b\[[0-9;]*m', '', line)) for line in lines) if lines else 0
        frame_width = min(max_content_width + 2, self.width)
        
        result = []
        
        top = "╔" + "═" * (frame_width - 2) + "╗"
        if title:
            title_text = f" {title} "
            padding = (frame_width - 2 - len(title_text)) // 2
            top = "╔" + "═" * padding + title_text + "═" * (frame_width - 2 - padding - len(title_text)) + "╗"
        result.append(top)
        
        for line in lines:
            clean_len = len(re.sub(r'\x1b\[[0-9;]*m', '', line))
            padding = frame_width - 2 - clean_len
            if padding > 0:
                line = line + " " * padding
            result.append(f"║ {line} ║")
        
        result.append("╚" + "═" * (frame_width - 2) + "╝")
        
        return '\n'.join(result)


class TUIInputHandler:
    
    def __init__(self):
        self.key_bindings: Dict[str, Callable] = {}
        self.mouse_handlers: Dict[str, Callable] = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.running = True
        
    def bind_key(self, key: str, handler: Callable):
        self.mouse_handlers[event] = handler
    
    def handle_key(self, key: str) -> bool:
        self.mouse_x = x
        self.mouse_y = y
        
        handler_key = f"{button}"
        if handler_key in self.mouse_handlers:
            self.mouse_handlers[handler_key](x, y)
            return True
        return False
    
    def read_key(self) -> str:
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.renderer = TUIRenderer(width, height)
        
    def clear(self):
        if style:
            text = style.apply(text)
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if y + i >= self.height:
                break
            for j, char in enumerate(line):
                if x + j >= self.width:
                    break
                self.buffer[y + i][x + j] = char
    
    def draw_box(self, x: int, y: int, width: int, height: int, style: str = "single"):
        return '\n'.join(''.join(row) for row in self.buffer)
    
    def display(self):
    
    def __init__(self):
        self.events: Dict[str, List[Callable]] = {}
        
    def on(self, event: str, handler: Callable):
        if event in self.events:
            for handler in self.events[event]:
                handler(*args, **kwargs)


class TUIManager:
    
    _instance: Optional['TUIManager'] = None
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.canvas = TUICanvas(width, height)
        self.renderer = TUIRenderer(width, height)
        self.converter = HTMLToTUIConverter(width, height)
        self.input_handler = TUIInputHandler()
        self.event_manager = TUIEventManager()
        
        self.pages: Dict[str, str] = {}        self.current_page = ""
        self.running = False
        self.selected_index = 0
        self.nav_items: List[Dict] = []
        
    @classmethod
    def get_instance(cls, width: int = 80, height: int = 24) -> 'TUIManager':
        self.pages[path] = html_content
        self.current_page = path
    
    def navigate(self, path: str):
        if not self.current_page or self.current_page not in self.pages:
            return
        
        html = self.pages[self.current_page]
        output = self.renderer.render_with_frame(html, title=f"NebulaShell - {self.current_page}")
        
        self.canvas.clear()
        self.canvas.draw_text(output, 0, 0)
        self.canvas.display()
    
    def show_error(self, message: str):
        <html>
        <body>
            <h1>❌ 错误</h1>
            <p>{message}</p>
            <p>按任意键返回</p>
        </body>
        </html>
        self.load_page("/error", error_html)
        self.render_current()
    
    def setup_default_bindings(self):
        if self.current_page not in self.pages:
            return
        
        html = self.pages[self.current_page]
        converter = HTMLToTUIConverter(self.width, self.height)
        converter.parse(html)
        
        for key, config in converter.get_keyboard_bindings().items():
            action = config.get('action', '')
            target = config.get('target', '')
            
            if action == 'navigate' and target:
                self.input_handler.bind_key(key, lambda t=target: self.navigate(t))
            elif action == 'quit':
                self.input_handler.bind_key(key, self.quit)
            elif action == 'refresh':
                self.input_handler.bind_key(key, self.render_current)
    
    def run_event_loop(self):
        self.running = False
    
    def start(self):
    global _tui_manager_instance
    if _tui_manager_instance is None:
        _tui_manager_instance = TUIManager(width, height)
    return _tui_manager_instance
