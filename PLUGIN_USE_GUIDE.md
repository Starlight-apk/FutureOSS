# 插件快捷引用指南 - use() 函数

## 🚀 极简使用方式

现在，在编写插件时，引用其他插件变得前所未有的简单！

### 一行代码搞定！

```python
# 在你的插件 main.py 中
from oss.plugin import use

# 获取其他插件实例
http_api = use("http-api")
database = use("database")
webui = use("webui")
```

就这么简单！不需要知道插件路径，不需要复杂配置！

---

## 📖 完整 API

### 1. `use(plugin_name)` - 获取插件实例

```python
from oss.plugin import use

# 直接使用
http_api = use("http-api")

# 安全检查后使用
if http_api:
    http_api.register_route("/my-route", handler)
```

### 2. `get_capability(capability_name)` - 按能力获取

```python
from oss.plugin import get_capability

# 获取提供 router 能力的插件
router = get_capability("router")

if router:
    router.add_route(...)
```

### 3. `has_plugin(plugin_name)` - 检查插件是否存在

```python
from oss.plugin import has_plugin, use

if has_plugin("database"):
    db = use("database")
    # 使用数据库...
else:
    print("数据库插件未安装")
```

### 4. `list_plugins()` - 列出所有已加载插件

```python
from oss.plugin import list_plugins

print(f"当前已加载 {len(list_plugins())} 个插件:")
for name in list_plugins():
    print(f"  - {name}")
```

---

## 💡 实际案例

### 案例 1: 在 HTTP 插件中注册路由

```python
"""我的业务插件"""
from oss.plugin import use

class MyPlugin:
    def init(self):
        # 获取 HTTP API 插件
        http_api = use("http-api")
        
        if http_api:
            # 注册路由
            http_api.register_route("GET", "/users", self.get_users)
            http_api.register_route("POST", "/users", self.create_user)
    
    def get_users(self, request):
        return {"users": [...]}
    
    def create_user(self, request):
        return {"success": True}
    
    def start(self):
        pass
    
    def stop(self):
        pass

def New():
    return MyPlugin()
```

### 案例 2: 使用数据库插件

```python
"""数据管理插件"""
from oss.plugin import use

class DataPlugin:
    def init(self):
        self.db = use("database")
        self.cache = use("cache")
    
    def start(self):
        if self.db:
            self.db.connect()
        
        if self.cache:
            self.cache.init()
    
    def get_data(self, key):
        # 先从缓存读取
        if self.cache:
            data = self.cache.get(key)
            if data:
                return data
        
        # 缓存未命中，从数据库读取
        if self.db:
            data = self.db.query("SELECT * FROM data WHERE key=?", key)
            # 写入缓存
            if self.cache and data:
                self.cache.set(key, data)
            return data
        
        return None
    
    def stop(self):
        if self.db:
            self.db.close()

def New():
    return DataPlugin()
```

### 案例 3: 条件依赖（可选插件）

```python
"""通知插件 - 可选依赖多个通知渠道"""
from oss.plugin import use

class NotificationPlugin:
    def init(self):
        # 这些插件可能存在，也可能不存在
        self.email = use("email-service")
        self.sms = use("sms-service")
        self.wechat = use("wechat-bot")
    
    def send_alert(self, message, user):
        results = []
        
        # 根据用户偏好和可用服务发送
        if user.prefer_email and self.email:
            results.append(self.email.send(user.email, message))
        
        if user.prefer_sms and self.sms:
            results.append(self.sms.send(user.phone, message))
        
        if user.prefer_wechat and self.wechat:
            results.append(self.wechat.send(user.wechat_id, message))
        
        return any(results)
    
    def start(self):
        pass
    
    def stop(self):
        pass

def New():
    return NotificationPlugin()
```

---

## 🔧 高级用法

### 自动重试获取插件

```python
from oss.plugin import use, has_plugin
import time

def wait_for_plugin(name, timeout=10):
    """等待插件加载完成"""
    start = time.time()
    while not has_plugin(name):
        if time.time() - start > timeout:
            return None
        time.sleep(0.1)
    return use(name)

# 使用
database = wait_for_plugin("database")
```

### 批量获取多个插件

```python
from oss.plugin import use

def get_plugins(*names):
    """批量获取插件"""
    return {name: use(name) for name in names}

# 使用
plugins = get_plugins("http-api", "database", "cache", "logger")

if plugins["http-api"] and plugins["database"]:
    # ...
    pass
```

---

## ⚠️ 注意事项

1. **加载时机**: 确保在其他插件加载完成后再调用 `use()`
   - 最好在 `init()` 或 `start()` 方法中使用
   - 不要在模块顶层直接调用

2. **返回值检查**: `use()` 可能返回 `None`（插件未加载）
   ```python
   http_api = use("http-api")
   if http_api:  # 始终检查！
       # 安全使用
       pass
   ```

3. **循环依赖**: 避免插件 A 依赖 B，B 又依赖 A 的情况

---

## 🎯 对比传统方式

### ❌ 以前的复杂方式
```python
import sys
from pathlib import Path

# 手动查找插件路径
store_dir = Path("store")
plugin_path = store_dir / "@{FutureOSS}" / "http-api" / "main.py"

# 手动导入
spec = importlib.util.spec_from_file_location("http_api", plugin_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# 创建实例
http_api = module.New()
```

### ✅ 现在的极简方式
```python
from oss.plugin import use
http_api = use("http-api")
```

**就是这么简单！** 🎉

---

## 📝 总结

| 功能 | 函数 | 示例 |
|------|------|------|
| 获取插件 | `use(name)` | `db = use("database")` |
| 按能力获取 | `get_capability(cap)` | `router = get_capability("router")` |
| 检查存在 | `has_plugin(name)` | `if has_plugin("db"): ...` |
| 列出插件 | `list_plugins()` | `print(list_plugins())` |

**核心思想：一行代码，搞定插件引用！**
