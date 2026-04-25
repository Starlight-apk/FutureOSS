"""配置管理测试"""
import os
import pytest
from pathlib import Path
import tempfile
import json

from oss.config.config import Config


class TestConfig:
    """配置管理测试类"""
    
    def test_default_values(self):
        """测试默认配置值"""
        config = Config()
        assert config.http_api_port == 8080
        assert config.http_tcp_port == 8082
        assert config.host == "0.0.0.0"
        assert config.log_level == "INFO"
        assert config.permission_check is True
    
    def test_env_override(self, monkeypatch):
        """测试环境变量覆盖"""
        monkeypatch.setenv("HTTP_API_PORT", "9999")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        config = Config()
        assert config.http_api_port == 9999
        assert config.log_level == "DEBUG"
    
    def test_file_config(self):
        """测试配置文件加载"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"HTTP_API_PORT": 7777, "LOG_LEVEL": "WARNING"}, f)
            temp_path = f.name
        
        try:
            config = Config(temp_path)
            assert config.http_api_port == 7777
            assert config.log_level == "WARNING"
        finally:
            os.unlink(temp_path)
    
    def test_env_priority_over_file(self, monkeypatch):
        """测试环境变量优先级高于配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"HTTP_API_PORT": 7777}, f)
            temp_path = f.name
        
        try:
            monkeypatch.setenv("HTTP_API_PORT", "8888")
            config = Config(temp_path)
            assert config.http_api_port == 8888  # 环境变量优先
        finally:
            os.unlink(temp_path)
            monkeypatch.delenv("HTTP_API_PORT", raising=False)
    
    def test_get_set(self):
        """测试 get/set 方法"""
        config = Config()
        assert config.get("HTTP_API_PORT") == 8080
        config.set("HTTP_API_PORT", 6666)
        assert config.get("HTTP_API_PORT") == 6666
    
    def test_properties(self):
        """测试属性访问"""
        config = Config()
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.store_dir, Path)
        assert config.data_dir.name == "data"
        assert config.store_dir.name == "store"
    
    def test_all_method(self):
        """测试 all() 方法返回所有配置"""
        config = Config()
        all_config = config.all()
        assert "HTTP_API_PORT" in all_config
        assert "HOST" in all_config
        assert len(all_config) > 5
    
    def test_bool_conversion(self, monkeypatch):
        """测试布尔值转换"""
        monkeypatch.setenv("PERMISSION_CHECK", "false")
        config = Config()
        assert config.permission_check is False
        
        monkeypatch.setenv("PERMISSION_CHECK", "true")
        config = Config()
        assert config.permission_check is True
    
    def test_int_conversion(self, monkeypatch):
        """测试整数转换"""
        monkeypatch.setenv("MAX_WORKERS", "8")
        config = Config()
        assert config.get("MAX_WORKERS") == 8
        
        # 无效值应该保持默认
        monkeypatch.setenv("MAX_WORKERS", "invalid")
        config = Config()
        assert config.get("MAX_WORKERS") == 4  # 默认值


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
