"""插件快捷引用模块 - 让插件间的依赖引用变得极简

使用方式（在插件的 main.py 中）:
    
    # 方式 1: 直接获取插件实例（最推荐）
    from oss.plugin import use
    http_api = use("http-api")
    
    # 方式 2: 获取特定能力
    from oss.plugin import get_capability
    router = get_capability("router")
    
    # 方式 3: 检查插件是否存在
    from oss.plugin import has_plugin
    if has_plugin("webui"):
        webui = use("webui")

就是这么简单！不需要知道插件在哪里，不需要复杂的路径！
"""
import sys
from typing import Any, Optional


def use(plugin_name: str) -> Optional[Any]:
    """获取已加载插件的实例
    
    Args:
        plugin_name: 插件名称（如 "http-api", "webui"）
        
    Returns:
        插件实例，如果插件未加载则返回 None
        
    Example:
        >>> from oss.plugin import use
        >>> http_api = use("http-api")
        >>> if http_api:
        ...     http_api.register_route(...)
    """
    # 从全局插件管理器获取
    _manager = _get_plugin_manager()
    if not _manager or plugin_name not in _manager.plugins:
        print(f"[use] 警告：插件 '{plugin_name}' 尚未加载")
        return None
    return _manager.plugins[plugin_name]["instance"]


def get_capability(capability_name: str) -> Optional[Any]:
    """获取提供特定能力的插件实例
    
    Args:
        capability_name: 能力名称（如 "router", "database"）
        
    Returns:
        提供该能力的插件实例，如果没有则返回 None
        
    Example:
        >>> from oss.plugin import get_capability
        >>> router = get_capability("router")
        >>> if router:
        ...     router.add_route(...)
    """
    _manager = _get_plugin_manager()
    if not _manager:
        return None
    return _manager.get_capability_provider(capability_name)


def has_plugin(plugin_name: str) -> bool:
    """检查插件是否已加载
    
    Args:
        plugin_name: 插件名称
        
    Returns:
        True 如果插件已加载，否则 False
        
    Example:
        >>> from oss.plugin import has_plugin
        >>> if has_plugin("database"):
        ...     db = use("database")
    """
    _manager = _get_plugin_manager()
    if not _manager:
        return False
    return plugin_name in _manager.plugins


def list_plugins() -> list[str]:
    """列出所有已加载的插件名称
    
    Returns:
        插件名称列表
        
    Example:
        >>> from oss.plugin import list_plugins
        >>> print(f"已加载插件：{list_plugins()}")
    """
    _manager = _get_plugin_manager()
    if not _manager:
        return []
    return list(_manager.plugins.keys())


def _get_plugin_manager():
    """获取全局插件管理器实例（内部方法）"""
    # 尝试从已加载的 plugin-loader 插件获取
    if 'plugin.plugin-loader' in sys.modules:
        module = sys.modules['plugin.plugin-loader']
        if hasattr(module, 'PluginLoaderPlugin'):
            # 查找已创建的实例
            for obj in module.__dict__.values():
                if isinstance(obj, module.PluginLoaderPlugin):
                    return obj.manager
    
    # 尝试从全局变量获取
    if '_futureoss_plugin_manager' in sys.modules:
        return sys.modules['_futureoss_plugin_manager']
    
    # 尝试从 oss 模块获取
    try:
        from oss import _plugin_manager
        return _plugin_manager
    except (ImportError, AttributeError):
        pass
    
    return None


# 向后兼容的别名
get_plugin = use
require = use
