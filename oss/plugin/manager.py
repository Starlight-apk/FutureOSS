"""插件管理器 - 只加载 plugin-loader，其他所有插件由 plugin-loader 插件自行管理"""
from typing import Any, Optional

from oss.plugin.loader import PluginLoader


class PluginManager:
    """极简插件管理器
    
    遵循「最小化核心框架」设计哲学：
    - 核心框架只负责加载 plugin-loader 插件
    - 所有其他插件（HTTP、WebSocket、Dashboard 等）都由 plugin-loader 插件扫描和加载
    - store/@{FutureOSS}/ 是唯一的插件来源
    """

    def __init__(self):
        self.loader = PluginLoader()
        self.plugin_loader: Optional[Any] = None

    def load(self):
        """仅加载 plugin-loader 核心插件
        
        plugin-loader 插件会负责：
        1. 扫描 store/@{FutureOSS}/ 目录
        2. 加载所有启用的插件
        3. 处理依赖关系
        4. 执行 PL 注入机制
        """
        # 只加载 plugin-loader，其他所有插件都由它来管理
        pl_info = self.loader.load_core_plugin("plugin-loader")
        if pl_info:
            self.plugin_loader = pl_info["instance"]

    def start(self):
        """启动 plugin-loader，它会初始化并启动所有其他插件"""
        if self.plugin_loader:
            # plugin-loader.init() 会扫描并加载 store/ 中的所有插件
            self.plugin_loader.init()
            # plugin-loader.start() 会按依赖顺序启动所有插件
            self.plugin_loader.start()

    def stop(self):
        """停止所有插件（由 plugin-loader 统一管理）"""
        if self.plugin_loader:
            try:
                self.plugin_loader.stop()
            except KeyboardInterrupt:
                print("[PluginManager] 用户中断停止过程")
            except Exception as e:
                import traceback
                print(f"[PluginManager] 停止插件时出错：{type(e).__name__}: {e}")
                traceback.print_exc()
