# 插件开发

## 目录结构

```
store/NebulaShell/your-plugin/
├── manifest.json       # 插件元数据与依赖声明（必需）
├── main.py             # 插件入口（必需）
└── SIGNATURE           # 签名文件（可选，签名验证用）
```

## manifest.json

```json
{
  "metadata": {
    "name": "your-plugin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "插件描述",
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

| 字段 | 说明 |
|------|------|
| `metadata.name` | 插件名，用于 `use()` 调用和依赖声明 |
| `metadata.type` | 插件类型：`core` 为核心插件，`plugin` 为普通插件 |
| `config.enabled` | 是否启用 |
| `dependencies` | 依赖的其他插件名列表 |
| `permissions` | 权限声明列表 |
| `metadata.load_priority` | 设为 `"first"` 可在插件加载器中优先加载 |

## main.py

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

### 生命周期

| 方法 | 调用时机 | 说明 |
|------|----------|------|
| `__init__` | 插件实例创建时 | 初始化成员变量，不要做耗时操作 |
| `init(deps)` | 所有插件加载后 | 初始化资源，此时可安全调用其他插件 |
| `start()` | 所有插件 init 完成后 | 启动服务、注册路由、开始监听 |
| `stop()` | 关闭时 | 清理资源、保存状态 |

## 使用其他插件

通过 `use()` 函数获取已加载的插件实例：

```python
from store.NebulaShell.plugin_bridge.main import use

class YourPlugin(Plugin):
    def init(self, deps: dict = None):
        storage = use("plugin-storage")
        if storage:
            storage.set("my_key", "my_value")

    def start(self):
        http_api = use("http-api")
        if http_api and hasattr(http_api, 'router'):
            http_api.router.get("/api/hello", self._hello_handler)

    def _hello_handler(self, request):
        from oss.plugin.types import Response
        return Response(status=200, body='{"message": "Hello"}',
                        headers={"Content-Type": "application/json"})
```

`use()` 会自动扫描 `store/` 下所有命名空间目录，读取 `manifest.json` 匹配插件名。已加载的插件会被缓存，不会重复加载。

## 注册 HTTP 路由

如果依赖了 `http-api` 插件，可以在其 router 上注册路由：

```python
http_api = use("http-api")
http_api.router.get("/api/my-endpoint", my_handler)
http_api.router.post("/api/my-endpoint", my_handler)
```

## 注册 WebUI 页面

如果依赖了 `webui` 插件，可以注册管理页面：

```python
webui = use("webui")
webui.register_page(
    path='/my-page',
    content_provider=my_content_provider,
    nav_item={'icon': 'ri-star-line', 'text': '我的页面'}
)
```

## 使用事件总线

`plugin-bridge` 提供事件总线，实现插件间解耦通信：

```python
bridge = use("plugin-bridge")
bridge.event_bus.on("user.login", self._on_user_login)
bridge.event_bus.emit(
    bridge.BridgeEvent(type="user.login", source_plugin="my-plugin")
)
```
