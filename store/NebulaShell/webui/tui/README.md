# NebulaShell TUI - 终端用户界面

## 概述

TUI（Terminal User Interface）插件为 NebulaShell 提供终端界面，与 WebUI 双启动运行。

## 核心特性

### 1. 转换层架构

TUI 本身只有一个转换层，它只会访问 WebUI 所开放的 `/tui` 接口：

- **`/tui/index.html`** - TUI 入口页面
- **`/tui/page`** - 获取任意页面的 TUI 版本
- **`/tui/css`** - 终端兼容的 CSS
- **`/tui/interact`** - 处理交互事件

### 2. HTML 标记规范

WebUI 开放的 `.html` 文件中不含有任何给用户看的内容，但包含 TUI 可解析的特殊标记：

```html
<!-- TUI 页面标记 -->
<html class="tui-page">
<body class="tui-body">

<!-- TUI 容器 -->
<div class="tui-container" data-tui-layout="vertical">

<!-- 键盘快捷键标记 -->
<a href="/" data-tui-key="1" data-tui-action="navigate">[1] 首页</a>

<!-- TUI 配置脚本 -->
<script type="application/x-tui-config">
{
    "keyboard": {
        "1": {"action": "navigate", "target": "/"},
        "q": {"action": "quit"}
    }
}
</script>

<!-- TUI CSS (仅终端支持的样式) -->
<style type="text/x-tui-css">
.tui-header { font-weight: bold; }
</style>
```

### 3. 支持的 CSS 属性

TUI 只支持终端能够渲染的样式：

| CSS 属性 | TUI 转换 | 说明 |
|---------|---------|------|
| `font-weight: bold` | ANSI 加粗 | `\x1b[1m` |
| `font-style: italic` | ANSI 斜体 | `\x1b[3m` |
| `text-decoration: underline` | ANSI 下划线 | `\x1b[4m` |
| `background-color` | ANSI 背景色 | 仅支持基础 8 色 |
| `color` | ANSI 前景色 | 仅支持基础 8 色 |
| `text-align` | 文本对齐 | left/center/right |

### 4. 支持的 JS 交互

TUI 只支持基础的终端交互：

- **鼠标位置** - 通过 ANSI 鼠标协议获取
- **点击事件** - 转换为选择操作
- **按键输入** - 完整的键盘支持

```javascript
// TUI 配置中的键盘映射
{
    "keyboard": {
        "1": {"action": "navigate", "target": "/"},
        "ArrowUp": {"action": "navigate_up"},
        "Enter": {"action": "select"},
        "q": {"action": "quit"}
    }
}
```

## 文件结构

```
webui/tui/
├── __init__.py          # 包初始化
├── main.py              # TUI 插件主程序
├── converter.py         # HTML 到 TUI 转换层
├── index.html           # TUI 入口页面（含特殊标记）
├── manifest.json        # 插件清单
└── README.md            # 本文档
```

## 使用方式

### 启动 NebulaShell

```bash
# 正常启动，WebUI 和 TUI 会同时运行
python main.py serve

# 或通过 CLI
python -m oss.cli serve
```

### TUI 快捷键

| 按键 | 功能 |
|-----|------|
| `1` | 首页 |
| `2` | 仪表盘 |
| `3` | 日志 |
| `4` | 终端 |
| `5` | 插件 |
| `6` | 设置 |
| `r` | 刷新 |
| `h` | 帮助 |
| `↑/↓` | 上下导航 |
| `Enter` | 确认 |
| `q` | 退出 TUI |

## 开发指南

### 创建 TUI 兼容页面

1. 在 WebUI 插件中创建页面时，添加 TUI 标记
2. 使用 `data-tui-*` 属性定义交互行为
3. 在 `<script type="application/x-tui-config">` 中定义键盘映射
4. 在 `<style type="text/x-tui-css">` 中定义终端样式

### 示例

```python
# 在 WebUI 插件中注册 TUI 兼容页面
def register_tui_page(webui):
    webui.register_page(
        path='/mypage',
        content_provider=lambda: '''
        <!DOCTYPE html>
        <html class="tui-page">
        <head><title>我的页面</title></head>
        <body class="tui-body">
            <div class="tui-container">
                <h1 data-tui-style="bold">欢迎</h1>
                <a href="/action" data-tui-key="a" data-tui-action="click">执行操作</a>
            </div>
            <script type="application/x-tui-config">
            {"keyboard": {"a": {"action": "click", "target": "/api/action"}}}
            </script>
        </body>
        </html>
        ''',
        nav_item={'icon': 'ri-star-line', 'text': '我的页面'}
    )
```

## 技术细节

### 转换流程

1. TUI 插件启动时访问 `/tui/index.html`
2. `HTMLToTUIConverter` 解析 HTML 提取：
   - 文本内容
   - 按钮和链接
   - TUI 配置（键盘映射、样式）
3. `TUIRenderer` 将元素渲染为 ANSI 转义序列
4. `TUICanvas` 管理终端显示缓冲区
5. `TUIInputHandler` 处理键盘/鼠标输入

### ANSI 颜色映射

```python
COLOR_MAP = {
    '#000000': '\x1b[30m',  # black
    '#ff0000': '\x1b[31m',  # red
    '#00ff00': '\x1b[32m',  # green
    '#ffff00': '\x1b[33m',  # yellow
    '#0000ff': '\x1b[34m',  # blue
    '#ff00ff': '\x1b[35m',  # magenta
    '#00ffff': '\x1b[36m',  # cyan
    '#ffffff': '\x1b[37m',  # white
}
```

## 许可证

MIT License - NebulaShell Project
