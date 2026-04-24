# FutureOSS - AI 专用项目介绍

## 项目概述

**FutureOSS** 是一个面向开发者的插件化运行时框架，采用「一切皆为插件」的设计理念。它是一个轻量级、安全、灵活的底层支撑系统，适用于构建微服务、开发工具链和可扩展的业务系统。

**核心设计哲学**：最小化核心框架，最大化插件扩展能力。核心框架仅提供最基本的插件加载和管理功能，所有其他功能（HTTP服务、Web界面、日志系统等）都通过插件实现。

## 技术栈

- **语言**: Python 3.10+
- **主要依赖**:
  - `click`: CLI 框架
  - `pyyaml`: 配置解析
  - `websockets`: WebSocket 支持
  - `psutil`: 系统监控
  - `cryptography`: 加密和签名验证
- **架构**: 插件化微内核架构
- **协议支持**: HTTP RESTful API, WebSocket, TCP HTTP
- **部署**: Docker 容器化支持

## 项目结构

```
/root/future-oss/
├── 📁 oss/                          # 核心框架代码
│   ├── cli.py                      # CLI 命令入口
│   ├── config/                     # 配置系统
│   ├── logger/                     # 日志系统
│   ├── plugin/                     # 插件框架核心
│   │   ├── capabilities.py         # 能力接口定义
│   │   ├── loader.py               # 插件加载器
│   │   ├── manager.py              # 插件生命周期管理
│   │   └── types.py                # 类型定义
│   └── shared/                     # 共享组件
│       └── router.py               # 统一路由系统
├── 📁 store/                       # 插件仓库（核心功能）
│   ├── @{FutureOSS}/              # 官方核心插件
│   │   ├── plugin-loader/         # 插件加载器（核心）
│   │   ├── http-api/              # HTTP API 服务
│   │   ├── http-tcp/              # TCP HTTP 服务
│   │   ├── ws-api/                # WebSocket API
│   │   ├── dashboard/             # Web 控制台
│   │   ├── dependency/            # 依赖解析
│   │   ├── signature-verifier/    # 签名验证
│   │   ├── plugin-bridge/         # 插件间通信
│   │   ├── plugin-storage/        # 数据持久化
│   │   ├── pkg-manager/           # 包管理
│   │   ├── log-terminal/          # 日志终端
│   │   ├── json-codec/            # JSON 编解码器
│   │   └── webui/                 # Web 用户界面
│   └── @{Falck}/                  # 社区插件
│       ├── html-render/           # HTML 渲染引擎
│       └── web-toolkit/           # Web 开发工具集
├── 📁 data/                        # 运行时数据目录
├── 📁 static/                      # 静态资源
├── 📁 templates/                   # 模板文件
├── 📁 tools/                       # 开发工具脚本
├── 📁 video/                       # 演示视频和文档
├── 📄 pyproject.toml              # Python 项目配置
├── 📄 requirements.txt             # Python 依赖
├── 📄 docker-compose.yml          # Docker 编排配置
├── 📄 Dockerfile                   # Docker 构建文件
├── 📄 README.md                    # 项目说明文档
└── 📄 LICENSE                      # Apache 2.0 许可证
```

## 核心架构

### 1. 插件系统架构

FutureOSS 采用三层插件架构：

1. **核心框架层** (`oss/`): 提供最基本的插件加载和管理能力
2. **核心插件层** (`store/@{FutureOSS}/`): 官方提供的核心功能插件
3. **社区插件层** (`store/@{Falck}/`): 第三方社区插件

### 2. 插件生命周期

```
加载 (load) → 初始化 (init) → 启动 (start) → 运行 (run) → 停止 (stop)
```

### 3. 插件元数据格式

每个插件必须包含 `manifest.json` 文件，格式如下：

```json
{
  "metadata": {
    "name": "插件名称",
    "version": "版本号",
    "author": "作者",
    "description": "功能描述",
    "type": "插件类型 (core/protocol/utility)"
  },
  "config": {
    "enabled": true/false,
    "args": {
      "参数名": "参数值"
    }
  },
  "dependencies": ["依赖插件列表"],
  "permissions": ["所需权限列表"]
}
```

### 4. 安全机制

- **数字签名验证**: 每个插件包含 SIGNATURE 文件
- **权限分级控制**: 插件声明所需权限
- **沙箱环境**: 可选的安全隔离
- **来源验证**: 插件作者命名空间 (@{作者名})

## 核心插件功能

### 系统核心插件

1. **plugin-loader**: 插件扫描、加载与生命周期管理（必需）
2. **http-api**: HTTP RESTful API 服务（端口 8080）
3. **http-tcp**: TCP 高性能 HTTP 服务（端口 8082）
4. **ws-api**: WebSocket API 服务（端口 8081）
5. **dashboard**: Web 可视化监控仪表盘
6. **dependency**: 插件依赖解析与自动安装
7. **signature-verifier**: 插件数字签名验证
8. **plugin-bridge**: 插件间通信桥接
9. **plugin-storage**: 插件数据持久化存储
10. **pkg-manager**: 插件包管理（安装/卸载/搜索）
11. **log-terminal**: 日志终端实时输出
12. **json-codec**: 统一 JSON 编解码器
13. **webui**: Web 用户界面框架

### 社区插件

1. **html-render**: HTML 模板渲染引擎
2. **web-toolkit**: Web 开发工具集（静态文件/模板/路由）

### 禁用插件（默认不加载）

1. **hot-reload**: 开发模式热重载
2. **i18n**: 国际化支持
3. **lifecycle**: 插件生命周期钩子
4. **code-reviewer**: 代码审查工具
5. **plugin-loader-pro**: 高级插件加载器

## PL 注入机制

PL 注入是 plugin-loader 插件提供的一种扩展机制，允许插件通过 `PL/` 文件夹向插件加载器注册自定义功能。

### 工作原理

插件加载器在启动时自动扫描所有插件，检查其 `manifest.json` 中是否声明了 `pl_injection` 配置项：

```
插件加载器启动
  ↓
扫描所有插件 manifest.json
  ↓
检查 config.args.pl_injection
  ├── true → 检查 PL/ 文件夹
  │     ├── 存在 PL/main.py → 沙箱执行 → 调用 register(injector) → ✅ 正常加载
  │     └── 缺少 PL/ 或 PL/main.py → ⚠️ 警告并 ❌ 拒绝加载
  └── false/未声明 → ✅ 正常加载（跳过 PL 检查）
```

### 使用方式

#### 1. 在 manifest.json 中声明

```json
{
  "config": {
    "args": {
      "pl_injection": true
    }
  }
}
```

#### 2. 创建 PL/main.py

```
store/@{作者名}/插件名/
├── manifest.json      # 声明 pl_injection: true
├── main.py            # 插件主逻辑
├── PL/                # PL 注入文件夹
│   └── main.py        # 注入逻辑（必须包含 register() 函数）
└── README.md
```

#### 3. 实现 register() 函数

```python
# PL/main.py
def register(injector):
    """向插件加载器注册功能
    
    Args:
        injector: PLInjector 实例
    """
    # 注册普通功能
    injector.register_function("my_helper", my_func, "功能描述")
    
    # 注册 HTTP 路由
    injector.register_route("GET", "/pl/hello", handler)
    
    # 注册事件处理器
    injector.register_event_handler("plugin.started", on_started)
```

### 注入器 API

| 方法 | 说明 |
|------|------|
| `register_function(name, func, description="")` | 注册注入功能 |
| `register_route(method, path, handler)` | 注册 HTTP 路由 |
| `register_event_handler(event_name, handler)` | 注册事件处理器 |
| `get_injected_functions(name=None)` | 获取已注册的注入功能 |
| `get_injection_info(plugin_name=None)` | 获取注入信息 |
| `has_injection(plugin_name)` | 检查插件是否有 PL 注入 |
| `get_registry_info()` | 获取注册表完整信息 |

### 安全限制

PL 注入机制实施了多层安全限制：

| 限制类型 | 具体措施 |
|---------|---------|
| **文件类型限制** | 禁止 PL 文件夹中包含 `.sh`、`.bat`、`.exe`、`.dll`、`.so` 等可执行文件 |
| **静态源码检查** | 编译前扫描源码，禁止导入 `os/sys/subprocess/socket/ctypes` 等系统模块，禁止 `exec/eval/compile/open/__import__` |
| **沙箱执行** | 在受限沙箱中执行 PL/main.py，仅提供安全的 builtins |
| **参数校验** | 功能名称、路由路径、HTTP 方法、事件名称均通过正则校验 |
| **数量限制** | 每个插件最多注册 50 个功能，每个名称最多被注册 10 次 |
| **异常安全** | 所有注册函数自动包装 try-catch，异常不影响主流程 |
| **调用者溯源** | 通过栈帧回溯自动识别调用者插件名，防止冒充注册 |

### 行为说明

| 场景 | 结果 |
|------|------|
| `pl_injection: true` + 存在 `PL/main.py` | ✅ 正常加载，执行注入 |
| `pl_injection: true` + 缺少 `PL/` 文件夹 | ❌ 警告并拒绝加载该插件 |
| `pl_injection: true` + 存在 `PL/` 但缺少 `main.py` | ❌ 警告并拒绝加载该插件 |
| 未声明 `pl_injection` | ✅ 正常加载，跳过 PL 检查 |
| `pl_injection: false` | ✅ 正常加载，跳过 PL 检查 |

## 开发与部署

### 开发环境设置

```bash
# 安装依赖
pip install -e .

# 启动开发服务器
oss serve

# 访问 Web 控制台
# http://localhost:8080
```

### Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 暴露端口
# 8080: HTTP API + 网站
# 8081: WebSocket
# 8082: HTTP TCP
```

### 插件开发

1. **创建插件目录**: `store/@{作者名}/{插件名}/`
2. **编写 manifest.json**: 定义插件元数据
3. **实现 main.py**: 插件主逻辑
4. **添加 SIGNATURE**: 数字签名（可选）
5. **测试插件**: 通过 pkg-manager 安装测试

## API 接口

### HTTP API (端口 8080)

- `GET /health`: 健康检查
- `GET /api/plugins`: 获取插件列表
- `GET /api/plugins/{name}`: 获取插件详情
- `POST /api/plugins/{name}/enable`: 启用插件
- `POST /api/plugins/{name}/disable`: 禁用插件

### WebSocket API (端口 8081)

- 实时日志推送
- 系统状态监控
- 插件事件通知

### TCP HTTP (端口 8082)

- 高性能 HTTP 服务
- 兼容 HTTP/1.1 协议

## 配置系统

### 配置文件位置

1. **全局配置**: `config.yaml` (可选)
2. **插件配置**: `store/@{作者名}/{插件名}/config.json`
3. **环境变量**: 支持 Docker 环境变量覆盖

### 配置优先级

```
环境变量 > 全局配置文件 > 插件默认配置
```

## 数据存储

### 数据目录结构

```
data/
├── html-render/     # 网站渲染文件
├── web-toolkit/     # Web 工具配置
├── plugin-storage/  # 插件持久化数据
└── DCIM/           # 共享资源存储
```

### 存储类型

1. **临时存储**: 内存缓存
2. **持久化存储**: 文件系统 (data/ 目录)
3. **插件私有存储**: 每个插件独立存储空间

## 监控与日志

### 日志系统

- **日志级别**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **输出目标**: 控制台、文件、WebSocket
- **日志格式**: 结构化 JSON 日志

### 监控指标

- 系统资源使用率 (CPU/内存/磁盘)
- 插件运行状态
- API 请求统计
- 错误率和异常监控

## 扩展能力

### 自定义插件开发

FutureOSS 支持多种插件类型：

1. **协议插件**: 实现网络协议 (HTTP/WebSocket/TCP)
2. **工具插件**: 提供开发工具功能
3. **界面插件**: 扩展 Web 控制台
4. **存储插件**: 实现数据存储后端
5. **中间件插件**: 请求处理管道

### 插件间通信

- **事件系统**: 发布/订阅模式
- **直接调用**: 通过插件管理器
- **共享存储**: 通过 plugin-storage
- **消息队列**: 通过 plugin-bridge

## 最佳实践

### 性能优化

1. **懒加载插件**: 按需加载非核心插件
2. **连接池管理**: 数据库和网络连接复用
3. **缓存策略**: 合理使用内存缓存
4. **异步处理**: I/O 密集型操作异步化

### 安全建议

1. **签名验证**: 生产环境启用所有插件签名验证
2. **权限最小化**: 插件只申请必要权限
3. **沙箱隔离**: 不可信插件启用沙箱模式
4. **定期更新**: 及时更新插件和安全补丁

### 高可用性

1. **健康检查**: 配置完整的健康检查端点
2. **故障转移**: 关键插件多实例部署
3. **监控告警**: 设置系统监控和告警
4. **备份恢复**: 定期备份插件配置和数据

## 故障排除

### 常见问题

1. **插件加载失败**: 检查 manifest.json 格式和依赖
2. **服务启动失败**: 检查端口冲突和权限
3. **性能问题**: 监控系统资源使用情况
4. **内存泄漏**: 检查插件资源释放

### 调试工具

1. **日志终端**: 实时查看系统日志
2. **Web 控制台**: 可视化监控插件状态
3. **API 接口**: 通过 REST API 获取系统信息
4. **开发工具**: tools/ 目录下的辅助脚本

## 官方网站项目

### 项目位置
`/root/future-oss/website/` - FutureOSS 官方宣传网站

### 技术栈
- **后端**: Node.js + Express.js
- **前端**: EJS 模板引擎 + 原生 JavaScript + CSS3
- **构建工具**: npm
- **开发工具**: VS Code 运行与调试配置

### 项目结构
```
website/
├── 📁 public/                    # 静态资源
│   ├── css/                     # 样式文件
│   │   ├── main.css            # 基础样式和变量
│   │   ├── components.css      # 组件样式
│   │   ├── animations.css      # 动画效果
│   │   └── pages/              # 页面特定样式
│   ├── js/                     # JavaScript 文件
│   │   ├── main.js             # 主逻辑
│   │   ├── router.js           # 前端路由
│   │   ├── animations.js       # 动画控制
│   │   └── pages/              # 页面特定脚本
│   └── images/                 # 图片资源
├── 📁 src/                      # 源代码
│   ├── server.js               # Express 服务器
│   ├── router.js               # 路由配置
│   ├── controllers/            # 控制器
│   │   ├── pagesController.js  # 页面控制器
│   │   └── apiController.js    # API 控制器
│   ├── middleware/             # 中间件
│   │   └── performance.js      # 性能优化中间件
│   ├── components/             # 组件（预留）
│   ├── pages/                  # 页面逻辑（预留）
│   └── styles/                 # 样式源码（预留）
├── 📁 views/                    # EJS 视图模板
│   ├── layouts/                # 布局文件
│   │   └── main.ejs            # 主布局
│   ├── pages/                  # 页面模板
│   │   ├── home.ejs            # 首页
│   │   ├── features.ejs        # 特性页
│   │   ├── architecture.ejs    # 架构页
│   │   └── plugins.ejs         # 插件页
│   └── partials/               # 局部组件
│       ├── navbar.ejs          # 导航栏
│       └── footer.ejs          # 页脚
├── 📄 package.json              # npm 配置
├── 📄 package-lock.json         # 依赖锁定
└── 📄 server.log                # 服务器日志
```

### 核心功能

#### 1. 多页面网站
- **首页** (`/`): 项目介绍和快速开始
- **特性页** (`/features`): 核心功能展示
- **架构页** (`/architecture`): 技术架构说明
- **插件页** (`/plugins`): 插件生态系统

#### 2. 性能优化特性
- **响应时间监控**: X-Response-Time 头部
- **缓存控制**: 静态资源长期缓存
- **压缩支持**: Gzip 和预压缩
- **安全头**: CSP、XSS 保护等
- **内存监控**: 实时内存使用监控

#### 3. 用户体验增强
- **加载动画**: 页面加载旋转指示器
- **页面切换动画**: 平滑的页面过渡效果
- **图片懒加载**: 延迟加载非视口图片
- **骨架屏**: 内容加载占位符
- **响应式设计**: 完整的移动端适配

#### 4. API 接口
- `GET /api/health`: 健康检查
- `GET /api/metrics`: 性能指标
- `GET /api/info`: 服务器信息
- `GET /api/stress-test`: 压力测试（仅开发环境）

### 技术特点

#### 服务器特性
- **端口自动切换**: 8080被占用时自动使用8081、8082等
- **优雅关闭**: 支持 SIGTERM/SIGINT 信号优雅关闭
- **错误处理**: 完善的错误处理和404页面
- **中间件栈**: 完整的性能优化中间件

#### 前端特性
- **组件化设计**: 导航栏、页脚等独立组件
- **前端路由**: 支持无刷新页面切换
- **CSS 变量**: 统一的主题变量系统
- **动画系统**: 丰富的CSS动画和过渡效果

#### 开发工具
- **VS Code 调试配置**: 支持直接运行与调试
- **热重载支持**: nodemon 开发模式
- **性能监控**: 实时性能指标输出
- **日志系统**: 结构化服务器日志

### 部署与运行

#### 开发模式
```bash
cd /root/future-oss/website
npm install
npm start
# 访问 http://localhost:8080 (或自动切换的端口)
```

#### 生产部署
```bash
# 使用 PM2 进程管理
pm2 start src/server.js --name "futureoss-website"

# 使用 Docker
docker build -t futureoss-website .
docker run -p 8080:8080 futureoss-website
```

#### VS Code 调试
1. 打开运行与调试面板 (Ctrl+Shift+D)
2. 选择 "FutureOSS 网站: 启动Node.js服务器"
3. 按 F5 启动调试

### 性能优化措施

#### 已实施的优化
1. **响应头优化**: 缓存控制、安全头、压缩头
2. **静态资源优化**: 长期缓存、预压缩支持
3. **代码分割**: 按页面加载CSS和JS
4. **图片优化**: 懒加载、占位符、响应式图片
5. **动画优化**: 减少重绘、will-change提示

#### 监控指标
- **响应时间**: X-Response-Time 头部
- **内存使用**: X-Memory-Usage 头部（开发环境）
- **慢响应日志**: 超过1秒的请求记录
- **错误率**: 500错误监控和记录

### 已知问题和解决方案

#### 1. ERR_HTTP_HEADERS_SENT 错误
- **问题**: 在响应已发送后设置响应头
- **原因**: `responseTime` 中间件在 `finish` 事件中设置头部
- **解决方案**: 使用 `headers` 事件或重写 `end` 方法
- **修复代码**:
  ```javascript
  // 错误写法（在 finish 事件中）:
  res.on('finish', () => {
    res.setHeader('X-Response-Time', `${duration}ms`); // 错误！
  });
  
  // 正确写法（重写 end 方法）:
  const originalEnd = res.end;
  res.end = function(...args) {
    if (!res.headersSent) {
      res.setHeader('X-Response-Time', `${duration}ms`);
    }
    return originalEnd.apply(this, args);
  };
  ```

#### 2. CSS 加载问题
- **问题**: 页面只显示纯文本，CSS未加载
- **原因**: EJS 布局系统未正确配置
- **解决方案**: 安装并配置 `express-ejs-layouts`
- **修复步骤**:
  1. `npm install express-ejs-layouts`
  2. 在 server.js 中添加中间件
  3. 设置默认布局 `app.set('layout', 'layouts/main')`

#### 3. 加载性能问题
- **问题**: 页面加载慢，无加载反馈
- **解决方案**: 添加加载动画和性能优化
- **实施措施**:
  1. 添加页面加载旋转动画
  2. 实现图片懒加载
  3. 添加骨架屏占位符
  4. 优化静态资源缓存

### 扩展和定制

#### 添加新页面
1. 在 `views/pages/` 创建新的 `.ejs` 文件
2. 在 `controllers/pagesController.js` 添加渲染函数
3. 在 `src/router.js` 添加路由
4. 在 `public/css/pages/` 添加页面特定CSS
5. 在 `public/js/pages/` 添加页面特定JS

#### 添加新组件
1. 在 `views/partials/` 创建组件 `.ejs` 文件
2. 在 `public/css/components.css` 添加组件样式
3. 在布局或页面中使用 `<%- include('partials/组件名') %>`

#### 主题定制
通过修改 CSS 变量实现主题切换：
```css
:root {
  --primary-color: #1e6fbb;    /* 主色调 */
  --text-primary: #333333;     /* 主要文字 */
  --bg-primary: #ffffff;       /* 背景色 */
  /* 更多变量... */
}
```

### 维护指南

#### 日常维护
1. **日志监控**: 定期检查 `server.log` 文件
2. **性能监控**: 关注慢响应日志
3. **错误处理**: 及时修复报告的错误
4. **依赖更新**: 定期更新 npm 包

#### 故障排除
1. **服务器无法启动**: 检查端口占用，查看日志
2. **页面样式异常**: 检查CSS文件路径和网络请求
3. **API 无响应**: 检查路由配置和控制器
4. **性能下降**: 使用 `/api/metrics` 接口诊断

#### 备份策略
1. **代码备份**: Git 版本控制
2. **配置备份**: 备份 `package.json` 和服务器配置
3. **数据备份**: 备份用户上传内容（如有）
4. **日志归档**: 定期归档服务器日志

## 未来发展方向

### 短期规划

1. 插件市场功能完善
2. 更多官方插件开发
3. 性能优化和稳定性提升
4. 官方网站功能增强

### 长期愿景

1. 跨语言插件支持
2. 云原生集成
3. 企业级功能扩展
4. 生态系统建设

## 注意事项

1. **生产部署**: 建议使用 Docker 容器化部署
2. **数据备份**: 定期备份 data/ 目录重要数据
3. **安全更新**: 关注安全公告并及时更新
4. **社区支持**: 通过 Gitee Issues 获取帮助
5. **网站维护**: 定期更新官方网站内容和功能

---

*本文件专为 AI 助手设计，提供 FutureOSS 项目的全面技术概述，帮助 AI 理解项目架构、功能和使用方式。更新日期：2026年4月19日*