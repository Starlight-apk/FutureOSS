"""插件加载器插件 - 支持能力扫描和扩展"""
import sys
import json
import importlib.util
from pathlib import Path
from typing import Any, Optional

from oss.plugin.types import Plugin, register_plugin_type
from oss.plugin.capabilities import scan_capabilities


class PluginInfo:
    """插件信息"""
    def __init__(self):
        self.name: str = ""
        self.version: str = ""
        self.author: str = ""
        self.description: str = ""
        self.readme: str = ""
        self.config: dict[str, Any] = {}
        self.extensions: dict[str, Any] = {}
        self.lifecycle: Any = None
        self.capabilities: set[str] = set()
        self.dependencies: list[str] = []


class PermissionError(Exception):
    """权限错误"""
    pass


class PluginProxy:
    """插件代理 - 防止越级访问"""

    def __init__(self, plugin_name: str, plugin_instance: Any, allowed_plugins: list[str], all_plugins: dict[str, dict[str, Any]]):
        self._plugin_name = plugin_name
        self._plugin_instance = plugin_instance
        self._allowed_plugins = set(allowed_plugins)
        self._all_plugins = all_plugins

    def get_plugin(self, name: str) -> Any:
        """获取其他插件实例（带权限检查）"""
        if name not in self._allowed_plugins and "*" not in self._allowed_plugins:
            raise PermissionError(f"插件 '{self._plugin_name}' 无权访问插件 '{name}'")
        if name not in self._all_plugins:
            return None
        return self._all_plugins[name]["instance"]

    def list_plugins(self) -> list[str]:
        """列出有权限访问的插件"""
        if "*" in self._allowed_plugins:
            return list(self._all_plugins.keys())
        return [name for name in self._allowed_plugins if name in self._all_plugins]

    def get_capability(self, capability: str) -> Any:
        """获取能力（带权限检查）"""
        # 能力访问不需要额外权限，能力注册表会自动处理
        return None

    def __getattr__(self, name: str):
        """代理其他属性到插件实例"""
        return getattr(self._plugin_instance, name)


class CapabilityRegistry:
    """能力注册表"""

    def __init__(self, permission_check: bool = True):
        self.providers: dict[str, dict[str, Any]] = {}
        self.consumers: dict[str, list[str]] = {}
        self.permission_check = permission_check

    def register_provider(self, capability: str, plugin_name: str, instance: Any):
        """注册能力提供者"""
        self.providers[capability] = {
            "plugin": plugin_name,
            "instance": instance,
        }
        if capability not in self.consumers:
            self.consumers[capability] = []

    def register_consumer(self, capability: str, plugin_name: str):
        """注册能力消费者"""
        if capability not in self.consumers:
            self.consumers[capability] = []
        if plugin_name not in self.consumers[capability]:
            self.consumers[capability].append(plugin_name)

    def get_provider(self, capability: str, requester: str = "", allowed_plugins: list[str] = None) -> Optional[Any]:
        """获取能力提供者实例（带权限检查）"""
        if capability not in self.providers:
            return None

        if self.permission_check and allowed_plugins is not None:
            provider_name = self.providers[capability]["plugin"]
            if provider_name != requester and provider_name not in allowed_plugins and "*" not in allowed_plugins:
                raise PermissionError(f"插件 '{requester}' 无权使用能力 '{capability}'")

        return self.providers[capability]["instance"]

    def has_capability(self, capability: str) -> bool:
        """检查是否有某个能力"""
        return capability in self.providers

    def get_consumers(self, capability: str) -> list[str]:
        """获取能力消费者列表"""
        return self.consumers.get(capability, [])


class PluginManager:
    """插件管理器"""

    def __init__(self, permission_check: bool = True):
        self.plugins: dict[str, dict[str, Any]] = {}
        self.lifecycle_plugin: Optional[Any] = None
        self._dependency_plugin: Optional[Any] = None  # dependency 插件引用
        self.capability_registry = CapabilityRegistry(permission_check=permission_check)
        self.permission_check = permission_check

    def set_lifecycle(self, lifecycle_plugin: Any):
        """设置生命周期插件"""
        self.lifecycle_plugin = lifecycle_plugin

    def _load_manifest(self, plugin_dir: Path) -> dict[str, Any]:
        """加载 manifest.json"""
        manifest_file = plugin_dir / "manifest.json"
        if not manifest_file.exists():
            return {}
        with open(manifest_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_readme(self, plugin_dir: Path) -> str:
        """加载 README.md"""
        readme_file = plugin_dir / "README.md"
        if not readme_file.exists():
            return ""
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()

    def _load_config(self, plugin_dir: Path) -> dict[str, Any]:
        """加载 Python 配置文件（带安全措施）"""
        config_file = plugin_dir / "config.py"
        if not config_file.exists():
            return {}

        safe_globals = {
            "__builtins__": {
                "True": True,
                "False": False,
                "None": None,
                "dict": dict,
                "list": list,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            }
        }
        local_vars = {}

        with open(config_file, "r", encoding="utf-8") as f:
            code = compile(f.read(), str(config_file), "exec")
            exec(code, safe_globals, local_vars)

        return {
            k: v for k, v in local_vars.items()
            if not k.startswith("_") and not callable(v)
        }

    def _load_extensions(self, plugin_dir: Path) -> dict[str, Any]:
        """加载扩展语法（Python 文件）"""
        ext_file = plugin_dir / "extensions.py"
        if not ext_file.exists():
            return {}

        safe_globals = {
            "__builtins__": {
                "True": True,
                "False": False,
                "None": None,
                "dict": dict,
                "list": list,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            }
        }
        local_vars = {}

        with open(ext_file, "r", encoding="utf-8") as f:
            code = compile(f.read(), str(ext_file), "exec")
            exec(code, safe_globals, local_vars)

        return {
            k: v for k, v in local_vars.items()
            if not k.startswith("_") and not callable(v)
        }

    def load(self, plugin_dir: Path, use_sandbox: bool = True) -> Optional[Any]:
        """加载单个插件"""
        main_file = plugin_dir / "main.py"
        if not main_file.exists():
            return None

        manifest = self._load_manifest(plugin_dir)
        readme = self._load_readme(plugin_dir)
        config = self._load_config(plugin_dir)
        extensions = self._load_extensions(plugin_dir)

        # 自动扫描能力
        capabilities = scan_capabilities(plugin_dir)

        plugin_name = plugin_dir.name
        
        # 清理插件名（去掉 } 后缀）
        plugin_name = plugin_dir.name.rstrip("}")

        # 解析权限
        permissions = manifest.get("permissions", [])

        # 沙箱加载
        if use_sandbox:
            from oss.plugin.loader import PluginLoader as FrameworkLoader
            framework_loader = FrameworkLoader(enable_sandbox=True)
            result = framework_loader.load_sandbox_plugin(plugin_dir)
            if not result:
                return None
            module = result["module"]
            instance = result["instance"]
        else:
            spec = importlib.util.spec_from_file_location(
                f"plugin.{plugin_name}", str(main_file)
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            if not hasattr(module, "New"):
                return None

            instance = module.New()

        # 创建代理包装器
        if self.permission_check and permissions:
            instance = PluginProxy(plugin_name, instance, permissions, self.plugins)

        info = PluginInfo()
        meta = manifest.get("metadata", {})
        info.name = meta.get("name", plugin_name)
        info.version = meta.get("version", "")
        info.author = meta.get("author", "")
        info.description = meta.get("description", "")
        info.readme = readme
        info.config = manifest.get("config", {}).get("args", config)
        info.extensions = extensions
        info.capabilities = capabilities
        info.dependencies = manifest.get("dependencies", [])

        # 注册能力
        for cap in capabilities:
            self.capability_registry.register_provider(cap, plugin_name, instance)

        # 创建生命周期
        if self.lifecycle_plugin and plugin_name != "lifecycle":
            lc = self.lifecycle_plugin.create(plugin_name)
            info.lifecycle = lc

        self.plugins[plugin_name] = {
            "instance": instance,
            "module": module,
            "info": info,
            "permissions": permissions,
        }
        return instance

    def load_all(self, store_dir: str = "store"):
        """加载 store 和 data/pkg 下所有插件（跳过自己）"""
        # 检查是否有任何插件存在
        has_plugins = self._check_any_plugins(store_dir)
        
        if not has_plugins:
            print("[plugin-loader] 未检测到任何插件，自动引导安装...")
            self._bootstrap_installation()

        # 可选：加载 lifecycle
        lifecycle_plugin = None
        lifecycle_dir = Path(store_dir) / "@{FutureOSS}" / "lifecycle"
        if lifecycle_dir.exists() and (lifecycle_dir / "main.py").exists():
            try:
                instance = self.load(lifecycle_dir)
                if instance:
                    lifecycle_plugin = instance
                    self.plugins.pop("lifecycle", None)
            except Exception:
                pass

        # 可选：加载 dependency
        dependency_plugin = None
        dependency_dir = Path(store_dir) / "@{FutureOSS}" / "dependency"
        if dependency_dir.exists() and (dependency_dir / "main.py").exists():
            try:
                instance = self.load(dependency_dir)
                if instance:
                    dependency_plugin = instance
                    self._dependency_plugin = instance  # 保存引用供拓扑排序使用
                    self.plugins.pop("dependency", None)
            except Exception:
                pass

        # 加载 lifecycle
        if lifecycle_plugin:
            self.set_lifecycle(lifecycle_plugin)

        # 加载其他插件
        self._load_plugins_from_dir(Path(store_dir))
        self._load_plugins_from_dir(Path("./data/pkg"))

        # 可选：按依赖排序
        if dependency_plugin:
            self._sort_by_dependencies(dependency_plugin)

    def _load_plugins_from_dir(self, store_dir: Path):
        """从指定目录加载插件"""
        if not store_dir.exists():
            return

        # 第一遍：加载所有插件
        for author_dir in store_dir.iterdir():
            if author_dir.is_dir():
                for plugin_dir in author_dir.iterdir():
                    if plugin_dir.is_dir() and plugin_dir.name not in ("plugin-loader", "lifecycle", "dependency"):
                        if (plugin_dir / "main.py").exists():
                            self.load(plugin_dir)

        # 第二遍：关联能力
        self._link_capabilities()

    def _check_any_plugins(self, store_dir: str) -> bool:
        """检查是否存在任何插件"""
        store = Path(store_dir)
        if store.exists():
            for author_dir in store.iterdir():
                if author_dir.is_dir():
                    for plugin_dir in author_dir.iterdir():
                        if plugin_dir.is_dir() and (plugin_dir / "main.py").exists():
                            return True
        
        pkg_dir = Path("./data/pkg")
        if pkg_dir.exists():
            for d in pkg_dir.iterdir():
                if d.is_dir() and (d / "main.py").exists():
                    return True
        
        return False

    def _bootstrap_installation(self):
        """引导安装 FutureOSS 官方插件"""
        # 加载 pkg 插件
        pkg_dir = Path("store/@{FutureOSS}/pkg")
        if pkg_dir.exists() and (pkg_dir / "main.py").exists():
            try:
                pkg_instance = self.load(pkg_dir, use_sandbox=False)
                if pkg_instance:
                    pkg_mgr = pkg_instance.manager
                    
                    print("[plugin-loader] 正在搜索可用插件...")
                    results = pkg_mgr.search()
                    if not results:
                        print("[plugin-loader] 未找到远程插件")
                        return
                    
                    print(f"[plugin-loader] 发现 {len(results)} 个插件，开始安装...")
                    installed_count = 0
                    for pkg_info in results:
                        print(f"[plugin-loader] 安装: {pkg_info.name}")
                        if pkg_mgr.install(pkg_info.name):
                            installed_count += 1
                    
                    if installed_count > 0:
                        print(f"[plugin-loader] 已安装 {installed_count} 个插件，重新扫描加载...")
                        # pkg 保留，重新加载其他插件
            except Exception as e:
                print(f"[plugin-loader] 引导安装失败: {e}")
        else:
            print("[plugin-loader] pkg 插件不存在，跳过引导安装")

    def _sort_by_dependencies(self, dep_plugin):
        """按依赖关系排序"""
        if not dep_plugin:
            return

        # 添加所有插件的依赖
        for name, info in self.plugins.items():
            deps = info["info"].dependencies
            dep_plugin.add_plugin(name, deps)

        try:
            order = dep_plugin.resolve()
            # 重新排序 plugins
            sorted_plugins = {}
            for name in order:
                if name in self.plugins:
                    sorted_plugins[name] = self.plugins[name]
            
            # 检查是否所有插件都在排序结果中
            missing = set(self.plugins.keys()) - set(sorted_plugins.keys())
            for name in missing:
                sorted_plugins[name] = self.plugins[name]
            
            self.plugins = sorted_plugins
        except Exception as e:
            print(f"[plugin-loader] 依赖解析失败: {e}")

    def _link_capabilities(self):
        """关联能力：带权限检查"""
        for plugin_name, info in self.plugins.items():
            caps = info["info"].capabilities
            allowed = info.get("permissions", [])
            
            for cap in caps:
                # 如果这个插件是某个能力的提供者
                if self.capability_registry.has_capability(cap):
                    # 找到所有需要这个能力的消费者
                    consumers = self.capability_registry.get_consumers(cap)
                    for consumer_name in consumers:
                        if consumer_name in self.plugins:
                            consumer_info = self.plugins[consumer_name]["info"]
                            consumer_allowed = self.plugins[consumer_name].get("permissions", [])
                            # 权限检查
                            try:
                                provider = self.capability_registry.get_provider(
                                    cap, 
                                    requester=consumer_name, 
                                    allowed_plugins=consumer_allowed
                                )
                                if provider and hasattr(consumer_info, "extensions"):
                                    consumer_info.extensions[f"_{cap}_provider"] = provider
                            except PermissionError as e:
                                print(f"[plugin-loader] 权限拒绝: {e}")

    def start_all(self):
        """启动所有插件（假设已初始化）"""
        # 注入依赖实例
        self._inject_dependencies()

        # 启动所有插件
        for name, info in self.plugins.items():
            try:
                info["instance"].start()
            except Exception as e:
                print(f"[plugin-loader] 启动失败 {name}: {e}")

    def init_and_start_all(self):
        """初始化并启动所有插件
        
        正确顺序：
        1. 注入依赖实例
        2. 按拓扑顺序 init() 所有插件
        3. 按拓扑顺序 start() 所有插件
        """
        print(f"[plugin-loader] init_and_start_all 被调用，plugins={len(self.plugins)}")
        
        # 1. 注入依赖实例
        self._inject_dependencies()

        # 2. 获取拓扑排序
        ordered_plugins = self._get_ordered_plugins()
        print(f"[plugin-loader] 插件启动顺序: {' -> '.join(ordered_plugins)}")

        # 3. 初始化所有插件（跳过 plugin-loader 自己）
        print("[plugin-loader] 开始初始化所有插件...")
        for name in ordered_plugins:
            if "plugin-loader" in name:
                continue
            info = self.plugins[name]
            try:
                print(f"[plugin-loader] 初始化: {name}")
                info["instance"].init()
            except Exception as e:
                print(f"[plugin-loader] 初始化失败 {name}: {e}")

        # 4. 启动所有插件（跳过 plugin-loader 自己）
        print("[plugin-loader] 开始启动所有插件...")
        for name in ordered_plugins:
            if "plugin-loader" in name:
                continue
            info = self.plugins[name]
            try:
                print(f"[plugin-loader] 启动: {name}")
                info["instance"].start()
            except Exception as e:
                print(f"[plugin-loader] 启动失败 {name}: {e}")

    def _get_ordered_plugins(self) -> list[str]:
        """获取按依赖排序的插件列表"""
        # 如果没有 dependency 插件，直接返回原始顺序
        if not hasattr(self, '_dependency_plugin') or not self._dependency_plugin:
            return list(self.plugins.keys())

        try:
            # 使用 dependency 插件解析
            order = self._dependency_plugin.resolve()
            # 过滤出实际存在的插件
            return [name for name in order if name in self.plugins]
        except Exception as e:
            print(f"[plugin-loader] 依赖解析失败，使用原始顺序: {e}")
            return list(self.plugins.keys())

    def _inject_dependencies(self):
        """注入插件依赖实例"""
        print(f"[plugin-loader] 开始注入依赖，共 {len(self.plugins)} 个插件")
        
        # 构建名称映射（处理 } 后缀问题）
        name_map = {}
        for name in self.plugins:
            clean = name.rstrip("}")
            name_map[clean] = name
            name_map[clean + "}"] = name
        
        for name, info in self.plugins.items():
            instance = info["instance"]
            info_obj = info.get("info")
            if not info_obj:
                continue
            deps = info_obj.dependencies
            if not deps:
                continue

            print(f"[plugin-loader] {name} 依赖: {deps}")
            for dep_name in deps:
                # 使用名称映射查找
                actual_dep = name_map.get(dep_name) or name_map.get(dep_name + "}")
                if actual_dep and actual_dep in self.plugins:
                    dep_instance = self.plugins[actual_dep]["instance"]
                    setter_name = f"set_{dep_name.replace('-', '_')}"
                    print(f"[plugin-loader] 尝试注入: {name} <- {actual_dep} ({setter_name})")
                    if hasattr(instance, setter_name):
                        try:
                            getattr(instance, setter_name)(dep_instance)
                            print(f"[plugin-loader] 注入成功: {name} <- {actual_dep}")
                        except Exception as e:
                            print(f"[plugin-loader] 注入依赖失败 {name}.{setter_name}: {e}")
                    else:
                        print(f"[plugin-loader] 警告: {name} 没有 {setter_name} 方法")

    def stop_all(self):
        """停止所有插件"""
        for name, info in reversed(list(self.plugins.items())):
            try:
                info["instance"].stop()
            except Exception:
                pass
        if self.lifecycle_plugin:
            self.lifecycle_plugin.stop_all()

    def get_info(self, name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        if name in self.plugins:
            return self.plugins[name]["info"]
        return None

    def has_capability(self, capability: str) -> bool:
        """检查系统是否有某个能力"""
        return self.capability_registry.has_capability(capability)

    def get_capability_provider(self, capability: str) -> Optional[Any]:
        """获取能力提供者"""
        return self.capability_registry.get_provider(capability)


class PluginLoaderPlugin(Plugin):
    """插件加载器插件"""

    def __init__(self):
        self.manager = PluginManager()
        self._loaded = False
        self._started = False

    def init(self, deps: dict = None):
        """加载所有插件"""
        if self._loaded:
            return
        self._loaded = True
        print("[plugin-loader] 开始加载插件...")
        self.manager.load_all()

    def start(self):
        """启动所有插件"""
        if self._started:
            return
        self._started = True
        print("[plugin-loader] 启动插件...")
        self.manager.init_and_start_all()

    def stop(self):
        """停止所有插件"""
        print("[plugin-loader] 停止插件...")
        self.manager.stop_all()


# 注册类型
register_plugin_type("PluginManager", PluginManager)
register_plugin_type("PluginInfo", PluginInfo)
register_plugin_type("CapabilityRegistry", CapabilityRegistry)


def New():
    return PluginLoaderPlugin()
