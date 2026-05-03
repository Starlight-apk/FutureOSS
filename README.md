# NebulaShell — 企业级插件化运行时框架

<div align="center">

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Status](https://img.shields.io/badge/build-passing-brightgreen)
![Plugins](https://img.shields.io/badge/plugins-26-informational)

**进程级隔离 · 声明式依赖管理 · 多语言运行时 · 热插拔架构**

[快速开始](#快速开始) · [架构](#架构设计) · [插件生态](#插件生态) · [开发指南](#开发你的第一个插件) · [贡献指南](#贡献指南)

</div>

---

## 项目简介

NebulaShell 是一个面向 **普通用户** 和 **开发者** 的企业级插件化运行时框架，旨在提供类似 Koishi Plus 的终端交互体验。核心设计哲学是「最小化核心」—— 所有功能皆由插件实现，系统核心仅保留最精简的加载与调度能力。

- **零配置部署**：安装即用，自动处理依赖关系
- **进程级隔离**：不可信插件运行在独立进程中，保障宿主安全
- **声明式依赖**：插件自行声明所需依赖，系统自动解析与安装
- **热插拔架构**：运行时动态加载/卸载/重载插件，业务零中断
- **多语言支持**：Python/Node.js/Go 等运行时无缝集成

---

## 快速开始

### 前置要求

- Python `>= 3.10`
- Linux / macOS / WSL2

### 安装与启动

```bash
# 克隆仓库
git clone https://github.com/Starlight-apk/NebulaShell.git
cd NebulaShell

# 安装依赖
pip install -r requirements.txt

# 启动核心
python main.py
```

启动后访问 [http://localhost:8080](http://localhost:8080) 进入管理控制台。

---

## 架构设计

```
用户/客户端
    │
    ▼
┌─────────────────────────────┐
│      HTTP API / WebSocket     │
│      (统一安全网关)           │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│       NebulaShell 微内核      │
│  ┌───────────────────────┐  │
│  │   Plugin Loader       │  │
│  │   • 插件发现与加载    │  │
│  │   • 依赖解析与注入    │  │
│  │   • 生命周期管理      │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
    │
    ├── 核心插件层 (可信域)
    │   ├── HTTP API 服务
    │   ├── WebSocket 服务
    │   ├── 数据持久化
    │   ├── 审计中心
    │   └── 监控探针
    │
    └── 隔离插件层 (不可信域)
        ├── 动态防火墙
        ├── 内网穿透
        ├── FTP 文件服务
        ├── 多语言运行时
        ├── 运维工具箱
        └── 安全网关
```

### 核心组件

| 组件 | 职责 | 技术选型 |
|------|------|----------|
| **Plugin Loader** | 插件发现、加载、依赖注入 | Python `importlib` + 进程隔离 |
| **Plugin Bridge** | 插件间通信（事件总线/RPC） | 自定义事件驱动架构 |
| **HTTP API** | RESTful API 网关 | Python `http.server` |
| **WebSocket API** | 实时双向通信 | 自定义 WebSocket 实现 |
| **WebUI** | 管理控制台 | 纯静态 HTML/CSS/JS |

---

## 插件生态

当前共有 **26 个官方插件**，涵盖基础设施、安全、网络、运维、开发者工具等领域。

### 基础设施

| 插件 | 描述 | 状态 |
|------|------|------|
| `plugin-loader` | 插件加载核心 | 稳定 |
| `plugin-bridge` | 插件间通信/事件总线/RPC | 稳定 |
| `plugin-storage` | 插件持久化存储 | 稳定 |
| `lifecycle` | 插件生命周期管理 | 稳定 |
| `hot-reload` | 热重载支持 | 稳定 |
| `i18n` | 国际化支持 | 稳定 |
| `dependency` | 依赖关系解析 | 稳定 |

### 网络与安全

| 插件 | 描述 | 状态 |
|------|------|------|
| `http-api` | RESTful API 服务 | 稳定 |
| `http-tcp` | TCP 协议适配 | 稳定 |
| `ws-api` | WebSocket 服务 | 稳定 |
| `firewall` | 动态防火墙 | Beta |
| `ftp-server` | FTP 文件服务 | Beta |
| `frp-proxy` | 内网穿透 | Beta |

### 运维与管理

| 插件 | 描述 | 状态 |
|------|------|------|
| `webui` | Web 管理控制台 | 稳定 |
| `dashboard` | 系统仪表盘 | 稳定 |
| `log-terminal` | 日志查看与 SSH 终端 | 稳定 |
| `pkg-manager` | 插件包管理器 | 稳定 |
| `auto-dependency` | 系统依赖自动安装 | 稳定 |
| `performance-optimizer` | 性能优化器 | Beta |

### 开发者工具

| 插件 | 描述 | 状态 |
|------|------|------|
| `code-reviewer` | 代码审查 | Beta |
| `nodejs-adapter` | Node.js 运行时适配 | Beta |
| `signature-verifier` | 插件签名验证 | 稳定 |
| `plugin-loader-pro` | 高级插件加载器（熔断/降级/容错） | Beta |

### 插件依赖管理

插件通过 `manifest.json` 声明其依赖关系，系统自动处理：

```json
{
  "metadata": {
    "name": "plugin-bridge",
    "version": "1.1.0",
    "type": "core"
  },
  "dependencies": ["plugin-storage", "i18n"],
  "permissions": ["plugin-storage", "lifecycle"]
}
```

依赖注入通过 `use()` 函数实现，无需硬编码路径：

```python
from store.NebulaShell.plugin_bridge.main import use

storage = use("plugin-storage")
i18n = use("i18n")
```

---

## 开发你的第一个插件

### 目录结构

```
store/NebulaShell/your-plugin/
├── manifest.json      # 插件元数据与依赖声明
├── main.py            # 插件入口
└── SIGNATURE          # 签名文件（可选）
```

### manifest.json

```json
{
  "metadata": {
    "name": "your-plugin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "你的插件描述",
    "type": "plugin"
  },
  "config": {
    "enabled": true,
    "args": {}
  },
  "dependencies": [],
  "permissions": []
}
```

### main.py

插件需实现 `Plugin` 基类，并暴露 `New()` 工厂函数：

```python
from oss.plugin.types import Plugin

class YourPlugin(Plugin):
    def init(self, deps: dict = None):
        pass

    def start(self):
        pass

    def stop(self):
        pass

def New():
    return YourPlugin()
```

### 使用其他插件

```python
from store.NebulaShell.plugin_bridge.main import use

class YourPlugin(Plugin):
    def init(self, deps: dict = None):
        http_api = use("http-api")
        if http_api:
            http_api.router.get("/api/your-endpoint", self.handler)
```

---

## 贡献指南

我们欢迎所有形式的贡献，包括但不限于：新功能、Bug 修复、文档改进、测试覆盖。

### 开发流程

1. Fork 仓库并创建特性分支
2. 编写代码并添加测试
3. 确保通过代码风格检查
4. 提交 Pull Request

### 提交规范

采用 Conventional Commits 规范：

```
feat: 新功能
fix: 修复 Bug
refactor: 代码重构
docs: 文档变更
test: 测试相关
chore: 构建/工具/依赖
```

---

## 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源。

---

<div align="center">

**Built with ❤️ by NebulaShell Team**

[GitHub](https://github.com/Starlight-apk/NebulaShell) · [Gitee](https://gitee.com/NebulaBase/NebulaShell)

</div>
