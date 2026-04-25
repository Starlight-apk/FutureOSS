# plugin-bridge 插件桥接器

**全局插件引用中心 - 让所有插件可以通过一行代码互相引用！**

## 🚀 核心功能

### 1. 极简插件引用（核心特性）

```python
# 在任何插件的 main.py 中，只需一行代码！
from plugin_bridge import use

# 引用其他插件
http_api = use("http-api")
database = use("database")
webui = use("webui")

# 直接使用
response = http_api.get("/api/users")
db = database.get_connection()
```

### 2. 事件总线（发布/订阅 + 解耦）

```python
bridge = plugin_mgr.get("plugin-bridge")
bus = bridge.event_bus

# 订阅事件（发布者和订阅者解耦）
bus.on("http.request", lambda event: print(f"收到请求：{event.payload}"))

# 发布事件
bus.emit(BridgeEvent(
    type="http.request",
    source_plugin="http-api",
    payload={"path": "/api/users"}
))
```

### 3. RPC 服务调用

```python
# 插件 B 注册服务
bridge.services.register("plugin-b", "get_user", lambda user_id: {"id": user_id, "name": "test"})

# 插件 A 调用插件 B 的服务
result = bridge.services.call("plugin-b", "get_user", 123)
print(result)  # {"id": 123, "name": "test"}
```

### 4. 广播

```python
broadcast = bridge.broadcast

# 创建频道
broadcast.create_channel("system", ["lifecycle", "metrics"])

# 广播消息
broadcast.broadcast("system", {"action": "shutdown"}, "plugin-loader")
```

### 5. 桥接

```python
bridge_mgr = bridge.bridge

# 创建桥接：将 http-api 的事件映射到 metrics
bridge_mgr.create_bridge(
    name="http-to-metrics",
    from_plugin="http-api",
    to_plugin="metrics",
    event_mapping={
        "http.request": "metrics.http_request",
        "http.error": "metrics.http_error",
    }
)
```

## 📦 API 参考

### 插件引用函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `use(name)` | 获取插件实例（不存在则抛出异常） | `http = use("http-api")` |
| `get_plugin(name)` | 安全获取插件（不存在返回 None） | `http = get_plugin("http-api")` |
| `has_plugin(name)` | 检查插件是否存在 | `if has_plugin("http-api"): ...` |
| `list_plugins()` | 列出所有可用插件 | `plugins = list_plugins()` |

### 管理函数（框架内部使用）

| 函数 | 说明 |
|------|------|
| `register_plugin(name, instance)` | 注册插件到全局注册表 |
| `unregister_plugin(name)` | 从全局注册表移除插件 |
| `set_plugin_instance(name, instance)` | 设置插件实例 |

## 🎯 使用场景

### 场景 1：在插件中使用 HTTP API

```python
from plugin_bridge import use

class MyPlugin(Plugin):
    def start(self):
        http = use("http-api")
        response = http.get("https://api.example.com/data")
        print(response)
```

### 场景 2：在插件中使用数据库

```python
from plugin_bridge import use

class DataPlugin(Plugin):
    def init(self):
        self.db = use("database")
    
    def process_data(self):
        conn = self.db.get_connection()
        results = conn.query("SELECT * FROM users")
        return results
```

### 场景 3：条件使用插件

```python
from plugin_bridge import use, has_plugin

class OptionalPlugin(Plugin):
    def start(self):
        if has_plugin("cache"):
            self.cache = use("cache")
        else:
            self.cache = None  # 降级处理
```

## ⚡ 优势

✅ **极简**：一行代码引用任何插件  
✅ **无需路径**：不需要知道插件的安装位置  
✅ **类型安全**：直接获取插件实例，支持自动补全  
✅ **第三方友好**：任何第三方插件都可以使用  
✅ **零配置**：无需任何配置文件  

## 🔧 事件历史

```python
# 查询历史
history = bus.get_history("http.request")

# 清空历史
bus.clear_history()
```
