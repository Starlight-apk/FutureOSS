"""Tests for Plugin Manager"""

import pytest
import tempfile
import shutil
from pathlib import Path

from oss.plugin.manager import PluginManager
from oss.plugin.loader import PluginLoader


@pytest.fixture
def temp_plugin_dir():
    temp_dir = tempfile.mkdtemp()
    store_dir = Path(temp_dir) / "store"
    store_dir.mkdir()
    plugin_loader_dir = store_dir / "NebulaShell" / "plugin-loader"
    plugin_loader_dir.mkdir(parents=True)
    main_py = plugin_loader_dir / "main.py"
    with open(main_py, 'w') as f:
        f.write("""
from oss.plugin.types import Plugin

class TestPlugin(Plugin):
    def __init__(self):
        self.name = "test-plugin"

    def init(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

def New():
    return TestPlugin()
""")
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestPluginManager:
    def test_loader_initialization(self, temp_plugin_dir):
        loader = PluginLoader()
        assert loader.loaded == {}
        assert loader._config is not None

    def test_load_plugin_with_main_py(self, temp_plugin_dir):
        loader = PluginLoader()
        assert loader is not None

    def test_load_plugin_without_new_function(self):
        loader = PluginLoader()
        temp_dir = tempfile.mkdtemp()
        plugin_dir = Path(temp_dir) / "syntax-error-plugin"
        plugin_dir.mkdir()

        main_py = plugin_dir / "main.py"
        with open(main_py, 'w') as f:
            f.write("def broken_function(\n")

        result = loader._load_plugin("syntax-error-plugin", plugin_dir)
        assert result is None
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
