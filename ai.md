# NebulaShell AI 开发文档

> **架构决策**：`nebula cli` 采用前后端分离设计，TUI 前端直连后端 JSON API，
> 不使用 HTML→ANSI 转换引擎。详见下文 [TUI 架构决策](#tui-架构决策)。

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

## TUI 架构决策

### 废弃方案：HTML→ANSI 动态转换层（v1.3）

**已废弃。** 早期方案通过 `oss/tui/converter.py`（1430 行）在运行时将 WebUI 的 HTML 页面解析为终端元素，存在以下问题：

| 问题 | 说明 |
|------|------|
| **布局失真** | CSS Flex/Grid 布局模型无法映射到终端字符网格 |
| **交互断层** | JavaScript 事件系统只能在终端模拟，与真实浏览器行为不一致 |
| **维护成本高** | 1430 行转换引擎 + 每个 WebUI 页面需维护 TUI 兼容标记 |
| **渲染性能差** | 每次导航需对整个 HTML 进行 DOM 解析和布局计算 |
| **调试困难** | 终端渲染错误难以定位是 HTML 问题还是转换器 Bug |

### 当前方案：前后端分离，原生 ANSI 渲染

```
nebula serve  ─── JSON API ───→  nebula cli (TUI 前端)
   (后端)                          (原生 ANSI 终端渲染)
```

**后端职责**（`nebula serve`）：
- 提供 RESTful JSON API（如 `/api/dashboard/stats`）
- WebSocket 实时推送
- 不感知 TUI 存在

**前端职责**（`nebula cli`）：
- 通过 HTTP/WebSocket 消费后端 JSON 数据
- 使用 ANSI 转义码直接在终端绘制界面
- 不依赖任何 HTML/CSS 解析

#### 技术要点

```
终端控制:
  raw mode  ───  tty.setraw()，单字节读取
  ONLCR     ───  重新开启 \n→\r\n 映射，避免阶梯乱码
  SGR 鼠标  ───  \x1b[?1000h\x1b[?1006h，解析 \x1b[<button;x;y;M
  SIGWINCH  ───  捕获终端 resize，全屏重绘

ANSI 绘制:
  24-bit 真彩色  ───  \x1b[38;2;R;G;Bm / \x1b[48;2;R;G;Bm
  字符图形        ───  █ ░ ▓ 等 Unicode 块字符作进度条
  光标定位        ───  \x1b[{row};{col}H

页面导航:
  热点区域映射    ───  预计算每行点击区域 (y → page_id)
  键盘备选       ───  数字键 1-5 作为鼠标候补
```

### 开放代码（opencode）TUI 架构分析

[opencode](https://opencode.ai) 是目前最成熟的终端 AI 编程助手，其 TUI 架构可参考：

| 特性 | opencode 实现 |
|------|-------------|
| **渲染引擎** | 原生终端渲染，无 HTML 中间层。直接操作终端缓冲区 |
| **组件系统** | 类似 React 的组件化方案，但所有组件直接输出 ANSI 字符串 |
| **输入处理** | raw mode + SGR 鼠标 + 组合键解析，支持 `Tab` 切换模式 |
| **布局** | 弹性布局引擎，组件根据终端宽度自动折行/折叠 |
| **状态管理** | 全局状态树，每次状态变更触发受控重绘（非全屏重绘）|
| **会话管理** | 多会话并行，每个会话独立维护上下文和渲染状态 |
| **主题系统** | 完整的配色方案，支持暗色/亮色主题切换 |

**关键差异**：opencode 不使用任何 Web 技术栈做 TUI，其所有界面元素（输入框、按钮、列表、状态栏、侧边栏）都是直接通过 ANSI 转义码在终端绘制的。每个组件是一个纯 Python/TypeScript 类，`render()` 方法返回 ANSI 字符串。

**对我们的启发**：
1. 放弃 HTML 转换层是正确的方向
2. 直接 ANSI 渲染的架构更可控、性能更好
3. 需要设计自己的组件化终端渲染库（参考 opencode 的组件系统）
4. `nebula cli` 命令已预留，后续在此框架上构建原生 TUI

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
