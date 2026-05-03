# HTTP API

`http-api` 插件提供 RESTful API 服务。启动后默认监听 `http://localhost:8080`。

## 路由

所有内置 API 端点以 `/api/` 开头。

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 系统状态（无需认证） |
| GET | `/api/health` | 健康检查 |

### 插件

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/plugins` | 列出所有已加载插件 |
| GET | `/api/plugins/{name}` | 获取插件信息 |
| POST | `/api/plugins/{name}/init` | 初始化插件 |
| POST | `/api/plugins/{name}/start` | 启动插件 |
| POST | `/api/plugins/{name}/stop` | 停止插件 |

### 仪表盘

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/stats` | 系统实时状态（CPU/内存/网络） |
| GET | `/api/dashboard/history` | 历史数据 |

### 包管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/packages/search` | 搜索可用插件 |
| GET | `/api/packages/list` | 列出已安装插件 |
| POST | `/api/packages/install` | 安装插件 |
| POST | `/api/packages/uninstall` | 卸载插件 |

### 国际化

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/i18n/locales` | 获取支持的语言列表 |
| GET | `/api/i18n/translate` | 翻译文本 |
| POST | `/api/i18n/locale` | 切换语言 |

## 认证

如果配置了 `API_KEY`，所有 API 请求需要在 Header 中携带：

```
Authorization: Bearer <your-api-key>
```

当 `API_KEY` 为空时，认证中间件自动禁用，所有端点公开访问。

## 自定义路由

在插件中注册自定义路由：

```python
from store.NebulaShell.plugin_bridge.main import use

http_api = use("http-api")
http_api.router.get("/api/my-endpoint", my_handler)
```
