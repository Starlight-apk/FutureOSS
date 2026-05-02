# NebulaShell AI 开发文档

## 项目介绍

NebulaShell 是一个企业级插件化运行时框架 (v1.2.0)，核心理念是「一切皆为插件」。它提供了一个最小化的核心系统，仅负责加载 `plugin-loader` 插件，其余 26+ 个官方插件均由该加载器管理。

### 核心特性

- **插件化架构**：所有功能均通过插件实现，支持热插拔
- **隐藏成就系统**：通过 `!!` 前缀访问的游戏化彩蛋（78+ 个验证规则）
- **智能依赖管理**：支持 6 大包管理器自动安装依赖
- **安全特性**：进程级隔离、PL 注入机制、签名验证、动态防火墙
- **双模界面**：同时支持 WebUI (浏览器) 和 TUI (终端) 双启动

### 技术栈

- Python 3.10+
- Click (命令行框架)
- PyYAML (配置解析)
- websockets (实时通信)
- Rich (TUI 渲染引擎)
- 纯静态 WebUI (HTML/CSS/JS)

---

## TUI + WebUI 双启动架构

### 架构概述

系统现在默认同时启动 WebUI 和 TUI：
- **WebUI**：在浏览器中运行，提供完整的图形界面
- **TUI**：在终端中运行，通过强大的转换层 (v1.3) 自动解析 WebUI 的 `/tui` 接口

### TUI 转换层核心能力 (v1.3)

TUI 转换层是一个强大的渲染引擎，能够自动访问 WebUI 开放的 `/tui` 接口，解析特殊的 `.html` 文件（入口为 `index.html`），并将其转换为终端界面。

#### 支持的组件类型 (64+)

```
基础组件: text, heading, paragraph, span, divider, spacer
容器组件: container, box, panel, card, grid, flex, stack
表单组件: input, button, checkbox, radio, select, textarea, slider
数据组件: table, list, tree, progress, gauge, chart, stat
导航组件: navbar, sidebar, menu, breadcrumb, tabs, pagination
反馈组件: alert, toast, modal, spinner, tooltip, badge
布局组件: row, col, section, article, aside, header, footer
特殊组件: code, pre, blockquote, mark, kbd, time, avatar
```

#### CSS 样式支持

转换层支持终端兼容的 CSS 样式：

```css
/* 颜色系统 */
color: #RGB, #RRGGBB, rgb(), rgba(), hsl(), 颜色名称
background-color: 同上
border-color: 同上

/* 字体排版 */
font-size: small, medium, large, x-large, numeric(pt)
font-weight: normal, bold, bolder, lighter, numeric(100-900)
font-style: normal, italic, oblique
text-decoration: none, underline, overline, line-through
text-align: left, center, right, justify

/* 边框样式 */
border: width style color
border-style: none, solid, double, dashed, rounded, heavy, ascii
border-width: thin, medium, thick, numeric
border-radius: numeric (仅支持 rounded 样式)

/* 布局与间距 */
margin: numeric
padding: numeric
width: numeric, percentage, auto
height: numeric, percentage, auto
display: block, inline, flex, grid, none

/* 特殊效果 */
opacity: 0.0-1.0 (通过字符密度模拟)
white-space: normal, nowrap, pre
overflow: visible, hidden, scroll
```

#### JavaScript 交互支持

转换层模拟基础 JS 交互功能：

```javascript
// 键盘事件
document.addEventListener('keydown', (e) => { ... })
document.addEventListener('keyup', (e) => { ... })

// 鼠标事件 (如果终端支持)
element.addEventListener('click', (e) => { ... })
element.addEventListener('mouseover', (e) => { ... })
element.addEventListener('mouseout', (e) => { ... })

// 焦点管理
element.focus()
element.blur()

// 类名切换
element.classList.add('active')
element.classList.remove('active')
element.classList.toggle('active')
```

### 使用方式

#### 启动服务

```bash
# 方式 1: 直接启动
python main.py

# 方式 2: 模块方式
python -m oss.cli serve

# 方式 3: Docker
docker run -p 8080:8080 nebulashell:latest
```

启动后：
- WebUI 自动在默认浏览器打开 (通常是 http://localhost:8080)
- TUI 在终端中自动渲染，显示相同内容

#### TUI 交互

- **方向键**：导航焦点元素
- **Enter/Space**：激活按钮/复选框
- **Tab/Shift+Tab**：切换焦点
- **q / Ctrl+C**：退出 TUI (WebUI 继续运行)
- **鼠标点击**：如果终端支持鼠标，可直接点击交互

#### 访问 /tui 接口

WebUI 需要开放 `/tui` 路径提供特殊 HTML：

```
GET /tui/index.html  - TUI 主页面
GET /tui/*.html      - 其他 TUI 页面
GET /tui/*.css       - TUI 专用样式
GET /tui/*.js        - TUI 交互逻辑
```

这些文件不包含给用户直接查看的内容，而是包含特殊的 `data-tui-*` 标记供转换层解析。

---

## 插件开发指南

### 插件基础结构

所有插件必须继承自 `oss.plugin.types.Plugin` 基类，并实现三个核心方法：

```python
from oss.plugin.types import Plugin
from oss.plugin.decorators import plugin

@plugin(name="my-plugin", version="1.0.0", description="我的插件")
class MyPlugin(Plugin):
    """插件类"""
    
    def init(self) -> None:
        """初始化阶段：加载配置、注册路由等"""
        self.logger.info("插件初始化")
        
    def start(self) -> None:
        """启动阶段：启动服务、连接数据库等"""
        self.logger.info("插件启动")
        
    def stop(self) -> None:
        """停止阶段：清理资源、断开连接等"""
        self.logger.info("插件停止")
```

### 插件目录结构

```
plugins/
└── my-plugin/
    ├── __init__.py          # 插件入口
    ├── plugin.py            # 主插件类
    ├── config.yaml          # 配置文件
    ├── routes/              # HTTP 路由
    │   ├── __init__.py
    │   └── api.py
    ├── tui/                 # TUI 专用页面
    │   ├── index.html
    │   ├── styles.css
    │   └── interaction.js
    ├── webui/               # WebUI 页面
    │   ├── index.html
    │   ├── styles.css
    │   └── app.js
    └── utils/               # 工具函数
        └── helpers.py
```

### 插件装饰器参数

```python
@plugin(
    name="unique-name",           # 唯一插件名 (必填)
    version="1.0.0",              # 版本号 (必填)
    description="插件描述",         # 描述 (必填)
    author="作者名",               # 作者 (可选)
    dependencies=["plugin-a"],    # 依赖插件列表 (可选)
    optional_dependencies=["plugin-b"],  # 可选依赖 (可选)
    min_core_version="1.0.0",     # 最低核心版本要求 (可选)
    tags=["category", "type"],    # 标签分类 (可选)
    enabled=True                  # 默认是否启用 (可选)
)
```

### 注册 HTTP 路由

```python
from flask import Blueprint, jsonify

# 创建路由蓝图
bp = Blueprint('my_plugin', __name__, url_prefix='/api/my-plugin')

@bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok", "plugin": "my-plugin"})

@bp.route('/data', methods=['POST'])
def receive_data():
    """接收数据接口"""
    data = request.json
    # 处理逻辑
    return jsonify({"success": True})

# 在插件的 init 方法中注册路由
def init(self) -> None:
    self.app.register_blueprint(bp)
```

### 创建 TUI/WebUI 页面

#### WebUI 页面 (webui/index.html)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>我的插件</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>欢迎使用我的插件</h1>
        <button id="action-btn">执行操作</button>
        <div id="result"></div>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

#### TUI 页面 (tui/index.html)

```html
<!-- TUI 专用页面，包含 data-tui 标记 -->
<div data-tui-type="panel" data-tui-title="我的插件" data-tui-border="rounded">
    <h1 data-tui-type="heading" data-tui-level="1" data-tui-align="center">
        欢迎使用我的插件
    </h1>
    
    <button 
        data-tui-type="button" 
        data-tui-label="执行操作"
        data-tui-id="action-btn"
        data-tui-style="primary">
    </button>
    
    <div 
        data-tui-type="text" 
        data-tui-id="result"
        data-tui-color="gray">
        等待操作...
    </div>
</div>
```

#### TUI 专用样式 (tui/styles.css)

```css
/* 仅包含终端支持的样式 */
.container {
    padding: 2;
    margin: 1;
}

h1 {
    font-size: large;
    font-weight: bold;
    text-align: center;
    color: #00ff00;
}

button {
    background-color: #0066cc;
    color: #ffffff;
    border: 2 solid #004499;
    border-style: rounded;
    padding: 1 2;
}

#result {
    color: #888888;
    font-style: italic;
}
```

#### TUI 交互逻辑 (tui/interaction.js)

```javascript
// 仅支持基础交互
document.getElementById('action-btn').addEventListener('click', function() {
    // 发送请求到后端
    fetch('/api/my-plugin/action', {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            document.getElementById('result').textContent = data.message;
        });
});

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    if (e.key === 'r') {
        // 刷新操作
        location.reload();
    }
});
```

### 插件配置

在 `config.yaml` 中定义插件配置：

```yaml
# plugins/my-plugin/config.yaml
plugin_name: my-plugin
enabled: true
settings:
  api_key: ""
  timeout: 30
  max_retries: 3
  debug: false
  
routes:
  prefix: /api/my-plugin
  auth_required: true

tui:
  enabled: true
  theme: default
  refresh_rate: 1000  # 毫秒

webui:
  enabled: true
  port: 8080
```

在插件中读取配置：

```python
def init(self) -> None:
    config = self.get_config()
    self.api_key = config.get('settings', {}).get('api_key', '')
    self.timeout = config.get('settings', {}).get('timeout', 30)
    self.logger.info(f"插件配置加载完成: timeout={self.timeout}")
```

### 插件间通信

```python
# 调用其他插件的方法
other_plugin = self.get_plugin('other-plugin')
if other_plugin:
    result = other_plugin.some_method(arg1, arg2)

# 发布事件
self.emit_event('my-event', {'data': 'value'})

# 订阅事件
@self.on_event('other-event')
def handle_event(event_data):
    self.logger.info(f"收到事件: {event_data}")
```

### 插件生命周期

```
1. 发现阶段：扫描 plugins 目录，识别插件
2. 排序阶段：根据依赖关系确定加载顺序
3. 初始化阶段：调用每个插件的 init() 方法
4. 启动阶段：调用每个插件的 start() 方法
5. 运行阶段：插件正常提供服务
6. 停止阶段：调用每个插件的 stop() 方法 (按依赖逆序)
```

### 调试插件

```bash
# 启用调试模式
export NEBULA_DEBUG=1
python main.py

# 查看特定插件日志
tail -f logs/nebula.log | grep my-plugin

# 热重载插件 (开发模式)
python main.py --dev --reload-plugins
```

### 打包插件

```bash
# 创建插件包
cd plugins/my-plugin
zip -r my-plugin-1.0.0.zip . 

# 安装插件
nebula plugin install my-plugin-1.0.0.zip

# 发布到插件市场
nebula plugin publish my-plugin-1.0.0.zip
```

---

## 最佳实践

### 1. 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 编写单元测试 (覆盖率 > 80%)
- 添加详细的文档字符串

### 2. 错误处理

```python
try:
    result = risky_operation()
except SpecificError as e:
    self.logger.error(f"操作失败: {e}")
    raise PluginError("操作执行失败", original_error=e)
finally:
    cleanup_resources()
```

### 3. 日志记录

```python
# 不同级别的日志
self.logger.debug("调试信息")
self.logger.info("一般信息")
self.logger.warning("警告信息")
self.logger.error("错误信息")
self.logger.critical("严重错误")

# 带上下文的日志
self.logger.info(
    "用户操作",
    extra={"user_id": user_id, "action": "create"}
)
```

### 4. 性能优化

- 使用异步操作处理 I/O 密集型任务
- 实现缓存机制减少重复计算
- 批量处理数据库操作
- 监控资源使用情况

### 5. 安全考虑

- 验证所有用户输入
- 使用参数化查询防止 SQL 注入
- 实施速率限制
- 定期更新依赖
- 敏感信息使用环境变量

---

## 常见问题

### Q: 如何禁用 TUI 只使用 WebUI？

```bash
# 设置环境变量
export NEBULA_TUI_ENABLED=false
python main.py

# 或在配置文件中
# config.yaml
tui:
  enabled: false
```

### Q: TUI 显示乱码怎么办？

确保终端支持 UTF-8 和真彩色：

```bash
# 检查终端支持
echo $TERM  # 应该类似 xterm-256color

# 启用真彩色
export COLORTERM=truecolor
```

### Q: 如何自定义 TUI 主题？

在插件的 `tui/styles.css` 中定义主题变量：

```css
:root {
    --primary-color: #0066cc;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --bg-color: #1a1a2e;
    --text-color: #eeeeee;
}
```

### Q: 插件加载失败如何排查？

```bash
# 查看详细日志
python main.py --verbose

# 检查插件依赖
nebula plugin check my-plugin

# 验证插件结构
nebula plugin validate my-plugin/
```

---

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/nebulashell/nebulashell.git
cd nebulashell

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black .
isort .
flake8 .
```

---

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

- 官网：https://nebulashell.io
- 文档：https://docs.nebulashell.io
- 社区：https://community.nebulashell.io
- GitHub: https://github.com/nebulashell/nebulashell
