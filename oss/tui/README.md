# TUI 转换层 - 强大的 WebUI 到终端界面转换引擎

## 架构设计

TUI 转换层是 NebulaShell 的核心组件之一，提供完整的 HTML/CSS/JS 到终端界面的转换能力。

### 核心理念

1. **只访问 WebUI 开放的 /tui 接口** - TUI 不直接渲染内容，而是通过 `/tui/*` 接口获取带有特殊标记的 HTML
2. **强大的转换层** - 自动解析 HTML 结构、CSS 样式、JS 交互配置，转换为终端元素
3. **参考 opencode 风格** - 提供现代化的终端用户体验

### 接口规范

#### `/tui/index.html` - TUI 入口
返回特殊标记的 HTML，不含用户可见内容，包含：
- `data-tui-*` 属性标记
- `<script type="application/x-tui-keys">` 键盘绑定配置
- `<script type="application/x-tui-config">` 显示配置
- `<style type="text/x-tui-css">` 终端兼容 CSS

#### `/tui/page?path=/xxx` - 获取任意页面
从 WebUI 获取原始 HTML，添加 TUI 标记后返回。

#### `/tui/css` - 终端兼容 CSS
只返回终端支持的 CSS 属性：
- 背景色（ANSI 颜色）
- 文字颜色（ANSI 颜色）
- 字体样式（bold, italic, underline）
- 边框样式

#### `/tui/js` - TUI 交互配置
模拟 JavaScript，仅支持：
- 获取鼠标位置
- 点击事件
- 按键事件

#### `/tui/interact` (POST) - 处理交互事件
接收 JSON 格式的事件数据：
```json
{"action": "navigate", "target": "/dashboard"}
{"action": "click", "target": "#button1"}
{"action": "keypress", "key": "q"}
```

#### `/tui/pages` - 列出可用页面
返回所有已注册页面的列表。

### HTML 标记规范

```html
<!-- TUI 页面标记 -->
<html class="tui-page" data-tui-version="2.0">

<!-- TUI 主体标记 -->
<body class="tui-body">

<!-- 布局容器 -->
<div data-tui-layout="vertical|horizontal|grid">

<!-- 元素类型 -->
<header data-tui-type="header">
<nav data-tui-type="nav">
<section data-tui-type="panel" data-tui-title="标题">
<button data-tui-key="q" data-tui-action="quit">
<a href="/page" data-tui-action="navigate" data-tui-key="1">

<!-- 分隔线 -->
<separator data-tui-char="─"/>

<!-- 键盘绑定配置 -->
<script type="application/x-tui-keys">
{"1": {"action": "navigate", "target": "/"}, "q": {"action": "quit"}}
</script>

<!-- 显示配置 -->
<script type="application/x-tui-config">
{"display": {"width": 80, "height": 24}, "mouse": {"enabled": true}}
</script>

<!-- 终端 CSS -->
<style type="text/x-tui-css">
.tui-page { background-color: #000000; color: #ffffff; }
.bold { font-weight: bold; }
</style>
```

### 支持的组件

| 组件 | HTML 标签 | 描述 |
|------|----------|------|
| 面板 | `<section data-tui-type="panel">` | 带边框的面板/卡片 |
| 按钮 | `<button data-tui-key="x">` | 可点击按钮，支持快捷键 |
| 列表 | `<ul>/<ol>` | 有序/无序列表 |
| 进度条 | `<div data-tui-type="progress">` | 进度条组件 |
| 加载动画 | `<div data-tui-type="spinner">` | 旋转加载器 |
| 导航 | `<nav data-tui-type="nav">` | 导航菜单 |
| 分隔线 | `<separator/>` | 水平分隔线 |

### 使用示例

```python
from oss.tui.converter import TUIManager, HTMLToTUIConverter

# 创建转换器
converter = HTMLToTUIConverter(width=80, height=24)

# 解析 HTML
html = """
<html class="tui-page">
<body class="tui-body">
    <h1>欢迎</h1>
    <button data-tui-key="q" data-tui-action="quit">退出 [q]</button>
    <script type="application/x-tui-keys">
    {"q": {"action": "quit"}}
    </script>
</body>
</html>
"""

layout = converter.parse(html)
output = layout.render()
print(output)

# 使用 TUI 管理器
manager = TUIManager.get_instance()
manager.load_page("/welcome", html)
manager.render_current()
manager.run_event_loop()
```

### 开发指南

1. **为 WebUI 页面添加 TUI 支持**
   - 在 HTML 中添加 `data-tui-*` 属性
   - 添加键盘绑定配置脚本
   - 确保 CSS 仅使用终端兼容属性

2. **创建新的 TUI 组件**
   - 继承 `TUIElement` 基类
   - 实现 `render()` 方法
   - 在 `HTMLToTUIConverter._create_tui_element()` 中注册

3. **扩展交互功能**
   - 在 `TUIInputHandler` 中添加新的事件处理器
   - 在 `/tui/interact` 接口中处理新的事件类型

## License

MIT License - NebulaShell Project
