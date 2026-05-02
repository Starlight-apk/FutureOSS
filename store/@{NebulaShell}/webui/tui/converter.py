"""TUI 转换层 - 强大的 WebUI 到终端界面转换引擎

本模块提供完整的 HTML/CSS/JS 到 TUI 的转换能力：
- HTML 解析：识别 data-tui-* 标记，转换为终端元素
- CSS 转换：仅支持终端兼容样式（ANSI 颜色、字体样式、边框）
- JS 交互：模拟鼠标位置、点击事件、键盘绑定
- 布局引擎：支持 flex/grid 布局的终端适配
- 组件系统：按钮、面板、列表、表单等终端组件

架构设计参考 opencode 风格，提供现代化终端体验。
"""
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
    """TUI 元素类型"""
    CONTAINER = "container"
    PANEL = "panel"
    BUTTON = "button"
    LABEL = "label"
    INPUT = "input"
    LIST = "list"
    LIST_ITEM = "list_item"
    SEPARATOR = "separator"
    HEADER = "header"
    FOOTER = "footer"
    NAV = "nav"
    TABLE = "table"
    PROGRESS = "progress"
    SPINNER = "spinner"


class ANSIStyle:
    """ANSI 样式常量"""
    RESET = '\x1b[0m'
    BOLD = '\x1b[1m'
    DIM = '\x1b[2m'
    ITALIC = '\x1b[3m'
    UNDERLINE = '\x1b[4m'
    BLINK = '\x1b[5m'
    REVERSE = '\x1b[7m'
    HIDDEN = '\x1b[8m'
    
    # 前景色
    FG_BLACK = '\x1b[30m'
    FG_RED = '\x1b[31m'
    FG_GREEN = '\x1b[32m'
    FG_YELLOW = '\x1b[33m'
    FG_BLUE = '\x1b[34m'
    FG_MAGENTA = '\x1b[35m'
    FG_CYAN = '\x1b[36m'
    FG_WHITE = '\x1b[37m'
    FG_DEFAULT = '\x1b[39m'
    
    # 背景色
    BG_BLACK = '\x1b[40m'
    BG_RED = '\x1b[41m'
    BG_GREEN = '\x1b[42m'
    BG_YELLOW = '\x1b[43m'
    BG_BLUE = '\x1b[44m'
    BG_MAGENTA = '\x1b[45m'
    BG_CYAN = '\x1b[46m'
    BG_WHITE = '\x1b[47m'
    BG_DEFAULT = '\x1b[49m'
    
    # 256 色支持
    @staticmethod
    def fg_256(color: int) -> str:
        return f'\x1b[38;5;{color}m'
    
    @staticmethod
    def bg_256(color: int) -> str:
        return f'\x1b[48;5;{color}m'


class BorderStyle:
    """边框样式"""
    NONE = ("", "", "", "", "", "", "", "")
    SINGLE = ("┌", "─", "┐", "│", "│", "└", "─", "┘")
    DOUBLE = ("╔", "═", "╗", "║", "║", "╚", "═", "╝")
    ROUNDED = ("╭", "─", "╮", "│", "│", "╰", "─", "╯")
    BOLD = ("┏", "━", "┓", "┃", "┃", "┗", "━", "┛")
    ASCII = ("+", "-", "+", "|", "|", "+", "-", "+")


@dataclass
class TUIStyle:
    """TUI 样式"""
    fg_color: str = ""
    bg_color: str = ""
    bold: bool = False
    dim: bool = False
    underline: bool = False
    italic: bool = False
    reverse: bool = False
    
    def apply(self, text: str) -> str:
        """应用样式到文本"""
        result = text
        if self.bold:
            result = f"{ANSIStyle.BOLD}{result}"
        if self.dim:
            result = f"{ANSIStyle.DIM}{result}"
        if self.underline:
            result = f"{ANSIStyle.UNDERLINE}{result}"
        if self.italic:
            result = f"{ANSIStyle.ITALIC}{result}"
        if self.reverse:
            result = f"{ANSIStyle.REVERSE}{result}"
        if self.fg_color:
            result = f"{self.fg_color}{result}"
        if self.bg_color:
            result = f"{self.bg_color}{result}"
        if any([self.bold, self.dim, self.underline, self.italic, self.reverse, self.fg_color, self.bg_color]):
            result = f"{result}{ANSIStyle.RESET}"
        return result


@dataclass
class TUIElement:
    """TUI 元素基类"""
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
        """渲染元素"""
        return self.style.apply(self.text)
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """获取边界 (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)


@dataclass
class TUIButton(TUIElement):
    """按钮"""
    action: str = ""
    target: str = ""
    clickable: bool = True
    shortcut: str = ""
    
    def render(self) -> str:
        text = self.text
        if self.shortcut:
            text = f"[{self.shortcut}] {text}"
        
        # 按钮样式
        btn_text = f"▌ {text} ▐"
        styled = self.style.apply(btn_text)
        
        # 填充到指定宽度
        padding = self.width - len(btn_text)
        if padding > 0:
            styled += " " * padding
        
        return styled


@dataclass
class TUILabel(TUIElement):
    """标签"""
    alignment: str = "left"  # left, center, right
    
    def render(self) -> str:
        text = self.style.apply(self.text)
        
        if self.alignment == "center":
            padding = (self.width - len(self.text)) // 2
            text = " " * padding + text
        elif self.alignment == "right":
            padding = self.width - len(self.text)
            text = " " * padding + text
        
        # 填充剩余空间
        remaining = self.width - len(self.text)
        if remaining > 0 and self.alignment == "left":
            text += " " * remaining
        
        return text


@dataclass
class TUIPanel(TUIElement):
    """面板/卡片"""
    border_style: str = "single"
    title: str = ""
    show_border: bool = True
    
    def render(self) -> str:
        borders = getattr(BorderStyle, self.border_style.upper(), BorderStyle.SINGLE)
        
        lines = []
        width = self.width - 2 if self.show_border else self.width
        
        # 顶部边框
        if self.show_border:
            if self.title:
                title_padding = (width - len(self.title)) // 2
                top = borders[0] + borders[1] * title_padding + f" {self.title} " + borders[1] * (width - title_padding - len(self.title) - 1) + borders[2]
            else:
                top = borders[0] + borders[1] * width + borders[2]
            lines.append(top)
        
        # 内容
        for child in self.children:
            content = child.render()
            if self.show_border:
                # 截断过长的内容
                content = content[:width].ljust(width)
                lines.append(f"{borders[3]} {content} {borders[4]}")
            else:
                lines.append(content)
        
        # 底部边框
        if self.show_border:
            bottom = borders[5] + borders[6] * width + borders[7]
            lines.append(bottom)
        
        return "\n".join(lines)


@dataclass
class TUILayout(TUIElement):
    """布局容器"""
    layout_type: str = "vertical"  # vertical, horizontal, grid
    gap: int = 1
    
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
    """列表"""
    items: List[str] = field(default_factory=list)
    selected_index: int = 0
    show_numbers: bool = True
    
    def render(self) -> str:
        lines = []
        for i, item in enumerate(self.items):
            prefix = f"{i + 1}. " if self.show_numbers else "  "
            marker = "► " if i == self.selected_index else "  "
            line = f"{marker}{prefix}{item}"
            if len(line) < self.width:
                line += " " * (self.width - len(line))
            lines.append(line[:self.width])
        return "\n".join(lines)


@dataclass
class TUISeparator(TUIElement):
    """分隔线"""
    char: str = "─"
    
    def render(self) -> str:
        return self.char * self.width


@dataclass
class TUIProgressBar(TUIElement):
    """进度条"""
    progress: float = 0.0  # 0.0 to 1.0
    filled_char: str = "█"
    empty_char: str = "░"
    
    def render(self) -> str:
        filled_width = int(self.width * self.progress)
        empty_width = self.width - filled_width
        bar = self.filled_char * filled_width + self.empty_char * empty_width
        percentage = f" {int(self.progress * 100)}%"
        return f"{bar}{percentage}"


@dataclass
class TUISpinner(TUIElement):
    """加载动画"""
    frames: List[str] = field(default_factory=lambda: ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    current_frame: int = 0
    
    def render(self) -> str:
        frame = self.frames[self.current_frame % len(self.frames)]
        return f"{frame} {self.text}"
    
    def next_frame(self):
        self.current_frame += 1


class HTMLToTUIConverter:
    """强大的 HTML 到 TUI 转换器
    
    支持：
    - 解析 HTML 结构和 data-tui-* 标记
    - 提取 CSS 样式并转换为 ANSI
    - 解析 JS 交互配置
    - 智能布局适配
    """
    
    COLOR_MAP = {
        '#000000': ANSIStyle.FG_BLACK,
        '#0000ff': ANSIStyle.FG_BLUE,
        '#008000': ANSIStyle.FG_GREEN,
        '#00ffff': ANSIStyle.FG_CYAN,
        '#ff0000': ANSIStyle.FG_RED,
        '#ff00ff': ANSIStyle.FG_MAGENTA,
        '#ffff00': ANSIStyle.FG_YELLOW,
        '#ffffff': ANSIStyle.FG_WHITE,
        '#808080': ANSIStyle.DIM,
        '#c0c0c0': ANSIStyle.FG_WHITE,
        'black': ANSIStyle.FG_BLACK,
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
        '#000000': ANSIStyle.BG_BLACK,
        '#0000ff': ANSIStyle.BG_BLUE,
        '#008000': ANSIStyle.BG_GREEN,
        '#00ffff': ANSIStyle.BG_CYAN,
        '#ff0000': ANSIStyle.BG_RED,
        '#ff00ff': ANSIStyle.BG_MAGENTA,
        '#ffff00': ANSIStyle.BG_YELLOW,
        '#ffffff': ANSIStyle.BG_WHITE,
        'black': ANSIStyle.BG_BLACK,
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
        """解析 HTML 并转换为 TUI 元素树"""
        # 移除 script 标签（除了 TUI 配置脚本）
        html_clean = self._extract_tui_scripts(html_content)
        html_no_script = re.sub(r'<script[^>]*>.*?</script>', '', html_clean, flags=re.DOTALL)
        
        # 提取 TUI 配置
        self._parse_tui_config(html_content)
        
        # 提取 CSS
        self._parse_tui_css(html_content)
        
        # 创建布局
        layout = TUILayout(layout_type="vertical")
        
        # 提取标题
        title_match = re.search(r'<title>(.*?)</title>', html_no_script, re.IGNORECASE)
        if title_match:
            header = TUILabel(
                text=title_match.group(1).strip(),
                style=TUIStyle(bold=True),
                width=self.width
            )
            layout.children.append(header)
            layout.children.append(TUISeparator())
        
        # 提取主体内容
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_no_script, re.IGNORECASE | re.DOTALL)
        if body_match:
            body_html = body_match.group(1)
            elements = self._parse_elements(body_html)
            layout.children.extend(elements)
        
        # 提取导航
        nav_elements = self._extract_nav(html_no_script)
        if nav_elements:
            layout.children.append(TUISeparator(char="─"))
            layout.children.append(TUILabel(text="导航菜单", style=TUIStyle(dim=True)))
            layout.children.extend(nav_elements)
        
        # 提取按钮
        btn_elements = self._extract_buttons(html_no_script)
        if btn_elements:
            layout.children.append(TUISeparator(char="─"))
            layout.children.extend(btn_elements)
        
        return layout
    
    def _extract_tui_scripts(self, html: str) -> str:
        """提取 TUI 配置脚本"""
        # 保存 TUI 配置脚本
        for match in re.finditer(r'<script[^>]*type=["\']application/x-tui-config["\'][^>]*>(.*?)</script>', html, re.DOTALL):
            try:
                config = json.loads(match.group(1).strip())
                if 'keyboard' in config:
                    self.keyboard_bindings = config['keyboard']
            except json.JSONDecodeError:
                pass
        return html
    
    def _parse_tui_config(self, html: str):
        """解析 TUI 配置"""
        for match in re.finditer(r'<script[^>]*type=["\']application/x-tui-config["\'][^>]*>(.*?)</script>', html, re.DOTALL):
            try:
                config = json.loads(match.group(1).strip())
                if 'keyboard' in config:
                    self.keyboard_bindings = config['keyboard']
                if 'mouse' in config:
                    mouse_config = config['mouse']
                    if mouse_config.get('enabled'):
                        self.mouse_handlers['click'] = lambda x, y: {'action': 'select'}
                if 'display' in config:
                    display = config['display']
                    self.width = display.get('width', self.width)
                    self.height = display.get('height', self.height)
            except json.JSONDecodeError:
                pass
    
    def _parse_tui_css(self, html: str):
        """解析 TUI CSS"""
        for match in re.finditer(r'<style[^>]*type=["\']text/x-tui-css["\'][^>]*>(.*?)</style>', html, re.DOTALL):
            css = match.group(1)
            # 简单的 CSS 解析
            for rule_match in re.finditer(r'([.#]?[\w-]+)\s*\{([^}]+)\}', css):
                selector = rule_match.group(1)
                properties = rule_match.group(2)
                style = self._parse_css_properties(properties)
                self.css_styles[selector] = style
    
    def _parse_css_properties(self, css_text: str) -> TUIStyle:
        """解析 CSS 属性为 TUI 样式"""
        style = TUIStyle()
        
        # 背景色
        bg_match = re.search(r'background(-color)?:\s*(#[0-9a-fA-F]{3,6}|[a-zA-Z]+)', css_text)
        if bg_match:
            color = bg_match.group(2).lower()
            style.bg_color = self.BG_COLOR_MAP.get(color, "")
        
        # 文字颜色
        color_match = re.search(r'color:\s*(#[0-9a-fA-F]{3,6}|[a-zA-Z]+)', css_text)
        if color_match:
            color = color_match.group(1).lower()
            style.fg_color = self.COLOR_MAP.get(color, "")
        
        # 字体样式
        if 'font-weight: bold' in css_text or 'font-weight:bold' in css_text:
            style.bold = True
        if 'font-style: italic' in css_text:
            style.italic = True
        if 'text-decoration: underline' in css_text:
            style.underline = True
        
        return style
    
    def _parse_elements(self, html: str) -> List[TUIElement]:
        """解析 HTML 元素"""
        elements = []
        
        # 解析带 data-tui-* 标记的元素
        for match in re.finditer(r'<(\w+)([^>]*)>(.*?)</\1>', html, re.DOTALL):
            tag = match.group(1)
            attrs_str = match.group(2)
            content = match.group(3)
            
            # 解析属性
            attrs = self._parse_attributes(attrs_str)
            
            # 检查是否是 TUI 元素
            if 'data-tui-type' in attrs or self._is_tui_element(tag, attrs):
                element = self._create_tui_element(tag, attrs, content)
                if element:
                    elements.append(element)
        
        # 也解析自闭合标签
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
        """解析 HTML 属性"""
        attrs = {}
        for match in re.finditer(r'([\w-]+)=["\']([^"\']*)["\']', attrs_str):
            key = match.group(1)
            value = match.group(2)
            attrs[key] = value
        
        # 处理布尔属性
        for match in re.finditer(r'([\w-]+)(?=\s|>|/>)', attrs_str):
            key = match.group(1)
            if key not in attrs:
                attrs[key] = True
        
        return attrs
    
    def _is_tui_element(self, tag: str, attrs: Dict) -> bool:
        """判断是否是 TUI 元素"""
        tui_tags = ['header', 'footer', 'nav', 'section', 'article', 'aside', 'main']
        tui_attrs = ['data-tui-type', 'data-tui-action', 'data-tui-key', 'data-tui-layout']
        
        return tag in tui_tags or any(attr in attrs for attr in tui_attrs)
    
    def _create_tui_element(self, tag: str, attrs: Dict, content: str) -> Optional[TUIElement]:
        """创建 TUI 元素"""
        # 清理 HTML 标签
        text = re.sub(r'<[^>]+>', '', content).strip()
        text = html.unescape(text)
        
        # 获取样式
        style = self._get_style_for_element(attrs)
        
        # 根据标签和属性创建元素
        tui_type = attrs.get('data-tui-type', '').lower()
        
        if tag == 'button' or tui_type == 'button' or 'data-tui-key' in attrs:
            return TUIButton(
                id=attrs.get('id', ''),
                text=text or attrs.get('data-tui-key', 'Button'),
                classes=attrs.get('class', '').split(),
                style=style,
                width=self.width,
                action=attrs.get('data-tui-action', ''),
                target=attrs.get('href', attrs.get('data-tui-target', '')),
                shortcut=attrs.get('data-tui-key', '')
            )
        
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header'] or tui_type == 'header':
            style.bold = True
            return TUILabel(
                id=attrs.get('id', ''),
                text=text,
                classes=attrs.get('class', '').split(),
                style=style,
                width=self.width,
                alignment="center" if tag == 'h1' else "left"
            )
        
        elif tag == 'nav' or tui_type == 'nav':
            # 导航特殊处理
            return None  # 由 _extract_nav 处理
        
        elif tag == 'hr' or tag == 'separator' or tui_type == 'separator':
            char = attrs.get('data-tui-char', '─')
            return TUISeparator(char=char, width=self.width)
        
        elif tag == 'ul' or tag == 'ol':
            items = []
            for li_match in re.finditer(r'<li[^>]*>(.*?)</li>', content, re.DOTALL):
                item_text = re.sub(r'<[^>]+>', '', li_match.group(1)).strip()
                items.append(html.unescape(item_text))
            return TUIList(items=items, width=self.width, show_numbers=(tag == 'ol'))
        
        elif tag == 'footer' or tui_type == 'footer':
            style.dim = True
            return TUILabel(
                id=attrs.get('id', ''),
                text=text,
                classes=attrs.get('class', '').split(),
                style=style,
                width=self.width
            )
        
        elif 'data-tui-layout' in attrs or tag in ['div', 'section', 'main', 'article']:
            layout_type = attrs.get('data-tui-layout', 'vertical')
            return TUILayout(
                id=attrs.get('id', ''),
                layout_type=layout_type,
                classes=attrs.get('class', '').split(),
                style=style,
                width=self.width
            )
        
        else:
            # 默认标签
            return TUILabel(
                id=attrs.get('id', ''),
                text=text,
                classes=attrs.get('class', '').split(),
                style=style,
                width=self.width
            )
    
    def _get_style_for_element(self, attrs: Dict) -> TUIStyle:
        """获取元素样式"""
        style = TUIStyle()
        
        # 检查 class
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
        
        # 检查 data-tui-style
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
        """提取导航元素"""
        elements = []
        
        for match in re.finditer(r'<nav[^>]*>(.*?)</nav>', html, re.DOTALL | re.IGNORECASE):
            nav_html = match.group(1)
            
            for link_match in re.finditer(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', nav_html, re.DOTALL | re.IGNORECASE):
                href = link_match.group(1)
                link_text = re.sub(r'<[^>]+>', '', link_match.group(2)).strip()
                link_text = html.unescape(link_text) if hasattr(html, 'unescape') else link_text
                
                # 获取快捷键
                attrs_str = link_match.group(0)
                shortcut = ""
                shortcut_match = re.search(r'data-tui-key=["\']([^"\']*)["\']', attrs_str)
                if shortcut_match:
                    shortcut = shortcut_match.group(1)
                
                btn = TUIButton(
                    text=f"{link_text}",
                    target=href,
                    shortcut=shortcut,
                    action="navigate",
                    width=self.width
                )
                elements.append(btn)
        
        return elements
    
    def _extract_buttons(self, html: str) -> List[TUIElement]:
        """提取按钮"""
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
        """获取键盘绑定"""
        return self.keyboard_bindings


class TUIRenderer:
    """TUI 渲染器"""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.converter = HTMLToTUIConverter(width, height)
        self.screen_buffer: List[List[str]] = []
        
    def render(self, html: str) -> str:
        """渲染 HTML 到终端字符串"""
        layout = self.converter.parse(html)
        return self.render_layout(layout)
    
    def render_layout(self, layout: TUILayout) -> str:
        """渲染布局"""
        self._init_buffer()
        self._render_element(layout, 0, 0)
        return self._buffer_to_string()
    
    def _init_buffer(self):
        """初始化缓冲区"""
        self.screen_buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
    
    def _render_element(self, element: TUIElement, x: int, y: int):
        """渲染元素到缓冲区"""
        rendered = element.render()
        lines = rendered.split('\n')
        
        for i, line in enumerate(lines):
            if y + i >= self.height:
                break
            
            # 清理 ANSI 码计算实际长度
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            
            for j, char in enumerate(line):
                if x + j >= self.width:
                    break
                self.screen_buffer[y + i][x + j] = char
    
    def _buffer_to_string(self) -> str:
        """缓冲区转字符串"""
        return '\n'.join(''.join(row) for row in self.screen_buffer)
    
    def render_with_frame(self, html: str, title: str = "NebulaShell TUI") -> str:
        """渲染带边框的页面"""
        content = self.render(html)
        lines = content.split('\n')
        
        # 计算最大宽度
        max_content_width = max(len(re.sub(r'\x1b\[[0-9;]*m', '', line)) for line in lines) if lines else 0
        frame_width = min(max_content_width + 2, self.width)
        
        result = []
        
        # 顶部
        top = "╔" + "═" * (frame_width - 2) + "╗"
        if title:
            title_text = f" {title} "
            padding = (frame_width - 2 - len(title_text)) // 2
            top = "╔" + "═" * padding + title_text + "═" * (frame_width - 2 - padding - len(title_text)) + "╗"
        result.append(top)
        
        # 内容
        for line in lines:
            clean_len = len(re.sub(r'\x1b\[[0-9;]*m', '', line))
            padding = frame_width - 2 - clean_len
            if padding > 0:
                line = line + " " * padding
            result.append(f"║ {line} ║")
        
        # 底部
        result.append("╚" + "═" * (frame_width - 2) + "╝")
        
        return '\n'.join(result)


class TUIInputHandler:
    """TUI 输入处理器
    
    支持：
    - 键盘事件（包括功能键、方向键）
    - 鼠标事件（点击、移动）
    - 自定义键绑定
    """
    
    def __init__(self):
        self.key_bindings: Dict[str, Callable] = {}
        self.mouse_handlers: Dict[str, Callable] = {}
        self.mouse_x = 0
        self.mouse_y = 0
        self.running = True
        
    def bind_key(self, key: str, handler: Callable):
        """绑定按键"""
        self.key_bindings[key] = handler
    
    def bind_mouse(self, event: str, handler: Callable):
        """绑定鼠标事件"""
        self.mouse_handlers[event] = handler
    
    def handle_key(self, key: str) -> bool:
        """处理按键"""
        if key in self.key_bindings:
            self.key_bindings[key]()
            return True
        return False
    
    def handle_mouse(self, x: int, y: int, button: str = 'left') -> bool:
        """处理鼠标"""
        self.mouse_x = x
        self.mouse_y = y
        
        handler_key = f"{button}"
        if handler_key in self.mouse_handlers:
            self.mouse_handlers[handler_key](x, y)
            return True
        return False
    
    def read_key(self) -> str:
        """读取按键（原始模式）"""
        import sys
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
            
            # 处理转义序列
            if char == '\x1b':
                char += sys.stdin.read(2)
            
            return char
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class TUICanvas:
    """TUI 画布"""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.renderer = TUIRenderer(width, height)
        
    def clear(self):
        """清屏"""
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
    
    def draw_text(self, text: str, x: int, y: int, style: TUIStyle = None):
        """绘制文本"""
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
        """绘制方框"""
        borders = getattr(BorderStyle, style.upper(), BorderStyle.SINGLE)
        
        # 顶边
        self.draw_text(borders[0] + borders[1] * (width - 2) + borders[2], x, y)
        
        # 侧边
        for i in range(1, height - 1):
            self.draw_text(f"{borders[3]}{' ' * (width - 2)}{borders[4]}", x, y + i)
        
        # 底边
        self.draw_text(borders[5] + borders[6] * (width - 2) + borders[7], x, y + height - 1)
    
    def render(self) -> str:
        """渲染画布"""
        return '\n'.join(''.join(row) for row in self.buffer)
    
    def display(self):
        """显示到终端"""
        sys.stdout.write('\x1b[2J\x1b[H')  # 清屏
        sys.stdout.write(self.render())
        sys.stdout.flush()


class TUIEventManager:
    """TUI 事件管理器"""
    
    def __init__(self):
        self.events: Dict[str, List[Callable]] = {}
        
    def on(self, event: str, handler: Callable):
        """注册事件处理器"""
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(handler)
    
    def emit(self, event: str, *args, **kwargs):
        """触发事件"""
        if event in self.events:
            for handler in self.events[event]:
                handler(*args, **kwargs)


class TUIManager:
    """TUI 管理器 - 核心管理类
    
    功能：
    - 页面管理
    - 渲染控制
    - 事件循环
    - 输入处理
    """
    
    _instance: Optional['TUIManager'] = None
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.canvas = TUICanvas(width, height)
        self.renderer = TUIRenderer(width, height)
        self.converter = HTMLToTUIConverter(width, height)
        self.input_handler = TUIInputHandler()
        self.event_manager = TUIEventManager()
        
        self.pages: Dict[str, str] = {}  # path -> html
        self.current_page = ""
        self.running = False
        self.selected_index = 0
        self.nav_items: List[Dict] = []
        
    @classmethod
    def get_instance(cls, width: int = 80, height: int = 24) -> 'TUIManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = TUIManager(width, height)
        return cls._instance
    
    def load_page(self, path: str, html_content: str):
        """加载页面"""
        self.pages[path] = html_content
        self.current_page = path
    
    def navigate(self, path: str):
        """导航到页面"""
        if path in self.pages:
            self.current_page = path
            self.render_current()
        else:
            self.show_error(f"Page not found: {path}")
    
    def render_current(self):
        """渲染当前页面"""
        if not self.current_page or self.current_page not in self.pages:
            return
        
        html = self.pages[self.current_page]
        output = self.renderer.render_with_frame(html, title=f"NebulaShell - {self.current_page}")
        
        self.canvas.clear()
        self.canvas.draw_text(output, 0, 0)
        self.canvas.display()
    
    def show_error(self, message: str):
        """显示错误"""
        error_html = f"""
        <html>
        <body>
            <h1>❌ 错误</h1>
            <p>{message}</p>
            <p>按任意键返回</p>
        </body>
        </html>
        """
        self.load_page("/error", error_html)
        self.render_current()
    
    def setup_default_bindings(self):
        """设置默认键绑定"""
        self.input_handler.bind_key('q', self.quit)
        self.input_handler.bind_key('Q', self.quit)
        self.input_handler.bind_key('\x03', self.quit)  # Ctrl+C
        self.input_handler.bind_key('\x04', self.quit)  # Ctrl+D
    
    def setup_keyboard_navigation(self):
        """从当前页面提取键盘绑定"""
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
        """运行事件循环"""
        self.running = True
        self.setup_default_bindings()
        
        while self.running:
            self.setup_keyboard_navigation()
            key = self.input_handler.read_key()
            self.input_handler.handle_key(key)
    
    def quit(self):
        """退出"""
        self.running = False
    
    def start(self):
        """启动 TUI"""
        if self.current_page:
            self.render_current()
            self.run_event_loop()


# 全局实例
_tui_manager_instance: Optional[TUIManager] = None


def get_tui_manager(width: int = 80, height: int = 24) -> TUIManager:
    """获取 TUI 管理器实例"""
    global _tui_manager_instance
    if _tui_manager_instance is None:
        _tui_manager_instance = TUIManager(width, height)
    return _tui_manager_instance
