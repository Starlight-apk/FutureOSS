Pytest configuration and shared fixtures

import os
import sys
import tempfile
import pytest
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def temp_data_dir():
    temp_dir = tempfile.mkdtemp()
    store_dir = Path(temp_dir) / "store"
    store_dir.mkdir()
    
    (store_dir / "@{NebulaShell}").mkdir()
    (store_dir / "@{Falck}").mkdir()
    
    yield str(store_dir)
    
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config(temp_data_dir, temp_store_dir):
    from oss.config.config import _global_config
    original_config = _global_config
    _global_config = None
    
    yield
    
    _global_config = original_config


@pytest.fixture
def sample_plugin_dir(temp_store_dir):
from oss.plugin.types import Plugin

class TestPlugin(Plugin):
    def __init__(self):
        self.name = "test-plugin"
        self.version = "1.0.0"
    
    def init(self):
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass

def New():
    return TestPlugin()
{
    "metadata": {
        "name": "test-plugin",
        "version": "1.0.0",
        "author": "Test Author",
        "description": "A test plugin"
    },
    "config": {
        "args": {
            "enabled": true
        }
    },
    "permissions": []
}
    plugin_dir = Path(sample_plugin_dir)
    
    pl_dir = plugin_dir / "PL"
    pl_dir.mkdir()
    
    pl_main = pl_dir / "main.py"
    with open(pl_main, 'w') as f:
        f.write(
import sys
import types
from typing import Any, Optional, Dict

from oss.plugin.types import Plugin, register_plugin_type

class Log:
    @classmethod
    def info(cls, tag: str, msg: str): print(f"[{tag}] {msg}")
    @classmethod
    def warn(cls, tag: str, msg: str): print(f"[{tag}] ⚠ {msg}")
    @classmethod
    def error(cls, tag: str, msg: str): print(f"[{tag}] ✗ {msg}")
    @classmethod
    def ok(cls, tag: str, msg: str): print(f"[{tag}] {msg}")

class PluginInfo:
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

class PluginManager:
    def __init__(self):
        self.plugins: dict = {}
        self.lifecycle_plugin = None
        self._dependency_plugin = None
        self._signature_verifier = None
    
    def load_all(self, store_dir: str = "store"):
        pass
    
    def init_and_start_all(self):
        pass
    
    def stop_all(self):
        pass

class PluginLoaderPlugin(Plugin):
    def __init__(self):
        self.manager = PluginManager()
        self._loaded = False
        self._started = False
    
    def init(self, deps: dict = None):
        if self._loaded: return
        self._loaded = True
        Log.info("plugin-loader", "开始加载插件...")
        self.manager.load_all()
    
    def start(self):
        if self._started: return
        self._started = True
        Log.info("plugin-loader", "启动插件...")
        self.manager.init_and_start_all()
    
    def stop(self):
        Log.info("plugin-loader", "停止插件...")
        self.manager.stop_all()

register_plugin_type("PluginManager", PluginManager)
register_plugin_type("PluginInfo", PluginInfo)

def New():
    return PluginLoaderPlugin()
    pass


def pytest_configure(config):
    for item in items:
        if "plugin_loader" in item.nodeid or "plugin_dir" in item.nodeid:
            item.add_marker(pytest.mark.plugin)
        
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)