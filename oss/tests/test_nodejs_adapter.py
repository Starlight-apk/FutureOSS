"""Tests for Node.js Adapter Plugin"""

import os
import sys
import json
import tempfile
import shutil
import pytest

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), '..', 'store', 'NebulaShell', 'nodejs-adapter')
sys.path.insert(0, PLUGIN_DIR)

import importlib.util
spec = importlib.util.spec_from_file_location("nodejs_adapter_main", os.path.join(PLUGIN_DIR, "main.py"))
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
NodeJSAdapter = main_module.NodeJSAdapter


@pytest.fixture
def adapter():
    return NodeJSAdapter()


@pytest.fixture
def temp_plugin_dir():
    temp_dir = tempfile.mkdtemp()
    pkg_dir = os.path.join(temp_dir, 'pkg')
    os.makedirs(pkg_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestNodeJSAdapter:
    def test_adapter_name(self, adapter):
        assert adapter.name == "nodejs-adapter"
        assert adapter.version == "1.0.0"
        assert "Node.js" in adapter.description

    def test_get_capabilities(self, adapter):
        versions = adapter.check_versions()
        assert isinstance(versions, dict)

    def test_init_hook(self):
        start = main_module.start
        context = {}
        result = start(context)
        assert result['status'] == 'inactive'

    def test_stop_hook(self):
        init = main_module.init
        get_info = main_module.get_info
        context = {}
        init(context)
        info = get_info(context)
        assert isinstance(info, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
