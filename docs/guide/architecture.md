# 架构说明

## 设计原则

NebulaShell 遵循「最小化核心」设计哲学：

- 核心框架（`oss/`）只负责加载 `plugin-loader` 这一个插件
- 所有功能皆由插件实现，包括 HTTP 服务、WebSocket、WebUI 等
- 插件加载器负责发现、加载、管理所有其他插件

## 架构分层

```
用户/客户端
    │
    ▼
┌─────────────────────────────┐
│   HTTP API / WebSocket      │  ← 由 http-api / ws-api 插件提供
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│   Plugin Loader             │  ← 由 oss/plugin/manager.py 加载
│   • 插件发现与加载          │
│   • 依赖解析与注入          │
│   • 生命周期管理            │
└─────────────────────────────┘
    │
    ├── 核心插件
    │   ├── plugin-bridge  插件间通信
    │   ├── lifecycle      生命周期
    │   ├── plugin-storage 持久化存储
    │   └── i18n           国际化
    │
    ├── 网络服务
    │   ├── http-api       RESTful API
    │   ├── ws-api         WebSocket
    │   └── http-tcp       TCP 适配
    │
    ├── 管理工具
    │   ├── webui          管理控制台
    │   ├── dashboard      系统仪表盘
    │   ├── log-terminal   日志终端
    │   └── pkg-manager    包管理
    │
    └── 扩展
        ├── firewall       防火墙
        ├── ftp-server     文件服务
        ├── frp-proxy      内网穿透
        └── ...
```

## 插件加载流程

1. `oss/plugin/manager.py` 通过 `PluginLoader` 加载 `plugin-loader` 插件
2. `plugin-loader` 扫描 `store/` 目录下所有插件的 `manifest.json`
3. 按 `load_priority` 排序，优先加载标记为 `"first"` 的插件（如 `plugin-bridge`）
4. 加载所有插件，解析 `dependencies` 字段并注入依赖
5. 按依赖顺序调用每个插件的 `init()` → `start()`

## 插件间通信

插件通过 `plugin-bridge` 提供的机制通信：

- **事件总线**：发布/订阅模式，解耦通信
- **服务注册表**：RPC 式服务调用
- **`use()` 函数**：直接获取已加载的插件实例

```python
from store.NebulaShell.plugin_bridge.main import use

storage = use("plugin-storage")
http_api = use("http-api")
```
