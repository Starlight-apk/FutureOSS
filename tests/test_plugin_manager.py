"""插件管理器单元测试"""
import pytest
from oss.plugin.manager import PluginManager


class TestPluginManager:
    """测试插件管理器核心功能"""

    def test_manager_initialization(self):
        """测试管理器初始化"""
        manager = PluginManager()
        assert manager.plugin_loader is None
        assert manager.loader is not None

    def test_manager_load(self):
        """测试管理器加载 plugin-loader"""
        manager = PluginManager()
        manager.load()
        
        assert manager.plugin_loader is not None
        assert hasattr(manager.plugin_loader, "init")
        assert hasattr(manager.plugin_loader, "start")
        assert hasattr(manager.plugin_loader, "stop")

    def test_manager_start_without_load(self):
        """测试未加载时启动（应安全处理）"""
        manager = PluginManager()
        # 不应抛出异常
        manager.start()

    def test_manager_stop_without_load(self):
        """测试未加载时停止（应安全处理）"""
        manager = PluginManager()
        # 不应抛出异常
        manager.stop()

    def test_manager_lifecycle(self):
        """测试完整生命周期"""
        manager = PluginManager()
        
        # 加载
        manager.load()
        assert manager.plugin_loader is not None
        
        # 启动（会初始化所有插件）
        # 注意：实际启动需要完整环境，这里只测试方法存在
        assert callable(manager.plugin_loader.init)
        assert callable(manager.plugin_loader.start)
        assert callable(manager.plugin_loader.stop)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
