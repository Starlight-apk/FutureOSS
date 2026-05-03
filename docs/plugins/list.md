# 插件列表

所有插件位于 `store/NebulaShell/` 目录下，每个插件包含 `manifest.json`（元数据）和 `main.py`（入口）。

## 基础设施

| 插件 | 说明 | 依赖 |
|------|------|------|
| plugin-loader | 插件加载核心，负责发现、加载、管理所有插件 | 无 |
| plugin-bridge | 插件间通信：事件总线、服务注册表、广播 | plugin-storage, i18n |
| plugin-storage | 插件持久化存储，提供键值存储和文件读写 | i18n |
| lifecycle | 插件生命周期管理，管理启动/停止顺序 | 无 |
| hot-reload | 文件变更监听，支持插件热重载 | 无 |
| i18n | 国际化支持，多语言翻译 | 无 |
| dependency | 依赖关系解析，拓扑排序 | 无 |

## 网络服务

| 插件 | 说明 | 依赖 |
|------|------|------|
| http-api | RESTful API 服务，路由注册与请求处理 | i18n |
| ws-api | WebSocket 服务，实时双向通信 | i18n |
| http-tcp | TCP 协议适配，将 TCP 连接转为 HTTP 请求 | i18n |

## 管理工具

| 插件 | 说明 | 依赖 |
|------|------|------|
| webui | Web 管理控制台，插件页面注册容器 | http-api, i18n |
| dashboard | 系统仪表盘，CPU/内存/网络实时监控 | http-api, webui |
| log-terminal | 日志查看器与 SSH 终端 | http-api, webui |
| pkg-manager | 插件包管理器，从 Gitee 仓库安装/卸载插件 | http-api, webui, plugin-storage, i18n |

## 安全

| 插件 | 说明 | 依赖 |
|------|------|------|
| signature-verifier | 插件签名验证，确保插件完整性 | plugin-storage, i18n |
| plugin-loader-pro | 高级插件加载器：熔断、降级、容错、自动修复 | plugin-loader |

## 开发者工具

| 插件 | 说明 | 依赖 |
|------|------|------|
| code-reviewer | 代码审查，检查代码质量、安全、风格 | 无 |
| nodejs-adapter | Node.js 运行时适配，在插件中运行 JavaScript | 无 |
| performance-optimizer | 性能优化器，缓存、对象池、字符串驻留 | 无 |
| auto-dependency | 系统依赖自动检测与安装 | plugin-loader |
| json-codec | JSON 编解码，提供高性能序列化 | 无 |

## 网络扩展

| 插件 | 说明 | 依赖 |
|------|------|------|
| firewall | 动态防火墙规则管理 | http-api, i18n |
| ftp-server | FTP 文件服务 | http-api, i18n |
| frp-proxy | FRP 内网穿透代理 | http-api, i18n |
| polyglot-deploy | 多语言项目部署（Python/Node.js/Go） | http-api, i18n, pkg-manager |

## 示例

| 插件 | 说明 | 依赖 |
|------|------|------|
| example-with-deps | 依赖声明示例（仅 manifest，无 main.py） | 无 |
