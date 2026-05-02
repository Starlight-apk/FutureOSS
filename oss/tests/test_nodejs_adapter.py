Tests for Node.js Adapter Plugin

import os
import sys
import json
import tempfile
import shutil
import pytest

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), '..', 'store', '@{NebulaShell}', 'nodejs-adapter')
sys.path.insert(0, PLUGIN_DIR)

import importlib.util
spec = importlib.util.spec_from_file_location("nodejs_adapter_main", os.path.join(PLUGIN_DIR, "main.py"))
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)
NodeJSAdapter = main_module.NodeJSAdapter


class TestNodeJSAdapter:
        return NodeJSAdapter()
    
    @pytest.fixture
    def temp_plugin_dir(self):
        assert adapter.name == "nodejs-adapter"
        assert adapter.version == "1.0.0"
        assert "Node.js" in adapter.description
    
    def test_get_capabilities(self, adapter):
        versions = adapter.check_versions()
        
        assert isinstance(versions, dict)
        if adapter.node_path:
            assert 'node' in versions
            assert not versions['node'].startswith('Error')
    
    def test_execute_in_context_missing_dir(self, adapter):
        if not adapter.node_path:
            pytest.skip("Node.js not available")
        
        result = adapter.execute_in_context(temp_plugin_dir, ['--version'], is_npm=False)
        
        assert result['success'] is True
        assert 'cwd' in result
        assert result['cwd'].endswith('pkg')
        assert result['stdout'].strip().startswith('v')
    
    def test_execute_in_context_npm_version(self, adapter, temp_plugin_dir):
        if not adapter.npm_path:
            pytest.skip("npm not available")
        
        result = adapter.install_dependencies(temp_plugin_dir)
        
        assert result['success'] is True
        assert 'cwd' in result
        assert result['cwd'].endswith('pkg')
    
    def test_run_script_test(self, adapter, temp_plugin_dir):
        if not adapter.node_path:
            pytest.skip("Node.js not available")
        
        js_file = os.path.join(temp_plugin_dir, 'pkg', 'hello.js')
        with open(js_file, 'w') as f:
            f.write("console.log('Hello from Node.js');")
        
        result = adapter.run_file(temp_plugin_dir, 'hello.js')
        
        assert result['success'] is True
        assert 'Hello from Node.js' in result['stdout']
    
    def test_init_project(self, adapter, temp_plugin_dir):
    
    def test_init_hook(self):
        start = main_module.start
        
        context = {}
        result = start(context)
        
        assert result['status'] == 'active'
    
    def test_stop_hook(self):
        init = main_module.init
        get_info = main_module.get_info
        
        context = {}
        init(context)
        
        info = get_info(context)
        
        assert isinstance(info, dict)
        assert 'features' in info or 'error' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
