"""插件加载器单元测试"""
import pytest
from pathlib import Path
from oss.plugin.loader import PluginLoader


class TestPluginLoader:
    """测试插件加载器核心功能"""

    def test_loader_initialization(self):
        """测试加载器初始化"""
        loader = PluginLoader()
        assert loader.loaded == {}

    def test_load_nonexistent_plugin(self):
        """测试加载不存在的插件"""
        loader = PluginLoader()
        result = loader.load_core_plugin("nonexistent-plugin")
        assert result is None

    def test_load_plugin_loader(self):
        """测试加载 plugin-loader 核心插件"""
        loader = PluginLoader()
        result = loader.load_core_plugin("plugin-loader")
        
        assert result is not None
        assert "instance" in result
        assert "module" in result
        assert "path" in result
        assert "name" in result
        assert result["name"] == "plugin-loader"
        assert hasattr(result["instance"], "init")
        assert hasattr(result["instance"], "start")
        assert hasattr(result["instance"], "stop")

    def test_loaded_plugins_tracking(self):
        """测试已加载插件跟踪"""
        loader = PluginLoader()
        initial_count = len(loader.loaded)
        
        loader.load_core_plugin("plugin-loader")
        
        assert len(loader.loaded) == initial_count + 1
        assert "plugin-loader" in loader.loaded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
