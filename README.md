<div align="center">
  <img src="static/banner.svg" alt="FutureOSS Banner" width="100%" />
</div>

<p align="center">
  <a href="https://gitee.com/starlight-apk/feature-oss"><img src="https://img.shields.io/badge/Gitee-代码仓库-C71D23?logo=gitee" alt="Gitee"></a>
  <a href="https://gitee.com/starlight-apk/feature-oss/wikis"><img src="https://img.shields.io/badge/文档-Wiki-4285F4?logo=readthedocs" alt="Wiki"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/许可证-Apache%202.0-green?logo=apache" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python" alt="Python">
</p>

---

## 🎯 项目简介

**FutureOSS** 是一款面向开发者的插件化运行时框架，秉承「**一切皆为插件**」的设计理念，让功能扩展变得前所未有的简单。

> 💡 无论是构建微服务、开发工具链，还是搭建可扩展的业务系统，FutureOSS 都能为你提供轻量、安全、灵活的底层支撑。

---

## ✨ 核心特性

| 特性 | 说明 |
|:---:|:---|
| 🔌 **插件化架构** | 核心功能全部插件化，按需加载，极致轻量 |
| 🛡️ **安全沙箱** | 数字签名验证 + 权限分级控制，确保插件来源可信 |
| 🔄 **热重载支持** | 开发阶段插件实时更新，无需重启服务 |
| 📊 **可视化控制台** | Web 仪表盘实时监控系统状态与插件运行情况 |
| 🌐 **双协议服务** | 同时支持 HTTP API 和 TCP 高性能模式 |
| 📦 **依赖自动解析** | 插件依赖自动安装，告别手动配置烦恼 |

---

## 🚀 快速开始

### 环境要求

- Python >= 3.10
- pip / uv

### 安装启动

```bash
# 克隆仓库
git clone https://gitee.com/starlight-apk/feature-oss.git
cd feature-oss

# 安装依赖
pip install -e .

# 启动服务
oss serve
```

服务启动后，访问 `http://localhost:8080` 即可进入 Web 控制台。

---

## 📂 项目结构

```
FutureOSS/
├── 🚀  pyproject.toml              # Python 项目配置
├── 📋  oss/                        # 核心框架包
│   ├── cli.py                      # CLI 命令入口
│   ├── config/                     # 配置系统
│   ├── logger/                     # 日志系统
│   ├── plugin/                     # 插件框架 (接口/加载器/管理器)
│   │   ├── capabilities.py         # 能力接口定义
│   │   ├── loader.py               # 插件加载器
│   │   ├── manager.py              # 插件生命周期管理
│   │   └── types.py                # 类型定义
│   └── shared/                     # 共享组件
│       └── router.py               # 统一路由系统
├── 🧩  store/                      # 本地插件仓库
│   └── @{作者名}/                  # 插件命名空间
│       └── {插件名}/               # 插件目录
│           ├── manifest.json       # 插件元数据
│           ├── main.py             # 插件入口
│           ├── config.json         # 插件配置
│           ├── README.md           # 插件文档
│           └── SIGNATURE           # 数字签名
├── 📦  data/                       # 运行时数据目录
│   ├── html-render/                # 网站渲染文件
│   ├── web-toolkit/                # Web 工具配置
│   ├── plugin-storage/             # 插件持久化存储
│   └── DCIM/                       # 共享资源存储
├── 🌐  website/                    # 官网 + 社区 (PHP)
├── 📖  static/                     # 静态资源
└── 🛠️  tools/                      # 开发工具脚本
```

---

## 🔌 内置核心插件

FutureOSS 采用「核心最小化 + 功能插件化」的设计，以下是框架自带的核心插件：

### 系统级插件 (@FutureOSS)

| 插件 | 状态 | 功能描述 |
|:---|:---:|:---|
| `plugin-loader` | ✅ | 插件扫描、加载与生命周期管理 |
| `dependency` | ✅ | 插件依赖解析与自动安装 |
| `signature-verifier` | ✅ | 插件数字签名验证 |
| `http-api` | ✅ | HTTP RESTful API 服务 |
| `http-tcp` | ✅ | TCP 高性能 HTTP 服务 |
| `json-codec` | ✅ | 统一 JSON 编解码器 |
| `plugin-bridge` | ✅ | 插件间通信桥接 |
| `plugin-storage` | ✅ | 插件数据持久化存储 |
| `pkg-manager` | ✅ | 插件包管理（安装/卸载/搜索） |
| `dashboard` | ✅ | Web 可视化监控仪表盘 |
| `log-terminal` | ✅ | 日志终端实时输出 |
| `hot-reload` | ⏸️ | 开发模式热重载（默认禁用） |
| `i18n` | ⏸️ | 国际化支持（默认禁用） |
| `lifecycle` | ⏸️ | 插件生命周期钩子（默认禁用） |

### 社区插件 (@Falck)

| 插件 | 功能描述 |
|:---|:---|
| `html-render` | HTML 模板渲染引擎 |
| `web-toolkit` | Web 开发工具集（静态文件/模板/路由） |

> **注**：插件名以 `.disabled` 结尾表示默认禁用，可通过配置启用。

---

## 📖 文档导航

完整开发者文档请查阅 [项目 Wiki](https://gitee.com/starlight-apk/feature-oss/wikis)：

| 📘 文档 | 📝 内容概要 |
|:---:|:---|
| [🎯 项目介绍](https://gitee.com/starlight-apk/feature-oss/wikis/项目介绍) | 架构设计、核心概念、设计理念 |
| [🚀 快速开始](https://gitee.com/starlight-apk/feature-oss/wikis/快速开始) | 安装指南、配置说明、首次运行 |
| [🔌 插件开发](https://gitee.com/starlight-apk/feature-oss/wikis/插件开发) | 编写第一个插件、事件系统、API 参考 |
| [📄 插件文档](https://gitee.com/starlight-apk/feature-oss/wikis/插件文档) | http-api、ws-api、file 等插件详解 |
| [📦 包管理](https://gitee.com/starlight-apk/feature-oss/wikis/包管理) | 插件安装/卸载/搜索/发布 |
| [⚙️ 配置参考](https://gitee.com/starlight-apk/feature-oss/wikis/配置参考) | 配置文件详解、参数说明 |
| [🚢 部署运维](https://gitee.com/starlight-apk/feature-oss/wikis/部署运维) | 本地运行、Docker、生产环境部署 |
| [🌟 社区与贡献](https://gitee.com/starlight-apk/feature-oss/wikis/社区与贡献) | 贡献指南、行为准则、开发规范 |

---

## 🔗 相关资源

<div align="center">

| 📦 代码仓库 | 📚 包仓库 | 🐛 问题反馈 |
|:---:|:---:|:---:|
| [Gitee](https://gitee.com/starlight-apk/feature-oss) | [Gitee Pkg](https://gitee.com/starlight-apk/future-oss-pkg) | [Issues](https://gitee.com/starlight-apk/feature-oss/issues) |

</div>

---

## 🛡️ 许可证与声明

### 开源许可

本项目采用 **[Apache License 2.0](LICENSE)** 开源许可证。

```
Copyright 2026 Falck

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

### 作者声明

> 以下声明作为 Apache 2.0 许可证的补充说明：

| 允许 ✅ | 禁止 🚫 |
|:---|:---|
| 个人学习、研究使用 | 未经书面许可的二次转发、搬运、转载 |
| 商业使用（保留版权声明） | 冒充原作者或声称与官方项目存在关联 |
| 修改和衍生作品 | 移除、修改或遮盖版权声明、许可证和 NOTICE 文件 |

> 此声明不改变 Apache 2.0 许可证的法律效力，仅表达作者的合理期望。如需特殊授权，请联系作者。

---

<div align="center">

<p>
  <strong>⚡ FutureOSS</strong> — 一切皆为插件
</p>

<p>
  Made with ❤️ by <a href="https://gitee.com/starlight-apk">Falck</a> & <a href="https://gitcode.com/yongwanxing">yongwanxing</a>
</p>

</div>
