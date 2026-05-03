# NebulaShell

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![build](https://img.shields.io/badge/build-passing-brightgreen)]()

NebulaShell 是一个插件化运行时框架。一切功能皆由插件实现，核心仅保留插件加载与调度能力。

---

## 快速开始

```bash
# 克隆
git clone https://github.com/Starlight-apk/NebulaShell.git
cd NebulaShell

# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

启动后访问 [http://localhost:8080](http://localhost:8080) 进入管理控制台。

---

## 插件

所有功能以插件形式提供，位于 `store/NebulaShell/` 目录下。当前内置 26 个插件。

| 插件 | 说明 |
|------|------|
| `plugin-loader` | 插件加载核心 |
| `plugin-bridge` | 插件间通信（事件总线 / RPC） |
| `http-api` | RESTful API 服务 |
| `ws-api` | WebSocket 服务 |
| `webui` | 管理控制台 |
| `dashboard` | 系统仪表盘 |
| `log-terminal` | 日志查看与终端 |
| `pkg-manager` | 插件包管理器 |
| `lifecycle` | 生命周期管理 |
| `i18n` | 国际化 |
| `plugin-storage` | 插件持久化存储 |
| `dependency` | 依赖关系解析 |
| `hot-reload` | 热重载 |
| `signature-verifier` | 签名验证 |
| `code-reviewer` | 代码审查 |
| `plugin-loader-pro` | 熔断/降级/容错 |
| `auto-dependency` | 系统依赖自动安装 |
| `performance-optimizer` | 性能优化 |
| `nodejs-adapter` | Node.js 运行时适配 |
| `http-tcp` | TCP 协议适配 |
| `firewall` | 防火墙 |
| `ftp-server` | 文件服务 |
| `frp-proxy` | 内网穿透 |
| `json-codec` | JSON 编解码 |
| `log-terminal` | 日志终端 |
| `polyglot-deploy` | 多语言部署 |

---

## 开发一个插件

在 `store/NebulaShell/` 下创建目录，包含 `manifest.json` 和 `main.py`：

```json
{
  "metadata": {
    "name": "my-plugin",
    "version": "1.0.0",
    "description": "我的插件"
  },
  "config": { "enabled": true, "args": {} },
  "dependencies": [],
  "permissions": []
}
```

```python
from oss.plugin.types import Plugin

class MyPlugin(Plugin):
    def init(self, deps=None):
        pass
    def start(self):
        pass
    def stop(self):
        pass

def New():
    return MyPlugin()
```

### 使用其他插件

通过 `use()` 获取已加载的插件实例：

```python
from store.NebulaShell.plugin_bridge.main import use

http_api = use("http-api")
webui = use("webui")
```

---

## 贡献

欢迎提交 Issue 和 Pull Request。

请确保代码通过语法检查：

```bash
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | \
  xargs -I{} python3 -m py_compile {}
```

---

## 许可证

Copyright 2026 Falck, yongwanxing

Licensed under the [Apache License, Version 2.0](LICENSE).
