"""插件管理器 - 只加载 plugin-loader"""
from typing import Any, Optional

from oss.plugin.loader import PluginLoader


class PluginManager:
    """管理基础插件"""

    def __init__(self):
        self.loader = PluginLoader()
        self.plugin_loader: Optional[Any] = None

    def load(self):
        """加载基础插件"""
        # 只加载 plugin-loader，其他都是可选的
        pl_info = self.loader.load_core_plugin("plugin-loader")
        if pl_info:
            self.plugin_loader = pl_info["instance"]

    def start(self):
        """启动基础插件"""
        if self.plugin_loader:
            self.plugin_loader.init()
            self.plugin_loader.start()

    def stop(self):
        """停止基础插件"""
        if self.plugin_loader:
            try:
                self.plugin_loader.stop()
            except Exception:
                pass
