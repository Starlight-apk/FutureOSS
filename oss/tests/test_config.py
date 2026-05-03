"""Tests for Configuration Management"""

import os
import json
import tempfile
import pytest
from pathlib import Path

from oss.config import Config, get_config, init_config


def temp_config_file():
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, "config.json")

    config_data = {
        "HTTP_API_PORT": 9000,
        "HTTP_TCP_PORT": 9002,
        "HOST": "127.0.0.1",
        "DATA_DIR": "./test_data",
        "STORE_DIR": "./test_store",
        "LOG_LEVEL": "DEBUG",
        "PERMISSION_CHECK": False,
        "MAX_WORKERS": 8,
        "API_KEY": "test-key",
        "CORS_ALLOWED_ORIGINS": ["http://localhost:8080"]
    }

    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    yield config_file

    os.remove(config_file)
    os.rmdir(temp_dir)


class TestConfig:
    def test_config_initialization_defaults(self):
        config = Config()
        assert config.get("LOG_LEVEL") == "INFO"

    def test_config_load_from_nonexistent_file(self):
        config = Config("/nonexistent/config.json")
        assert config.get("HTTP_API_PORT") == 8080

    def test_config_load_from_env(self):
        os.environ["HTTP_API_PORT"] = "7000"
        os.environ["HOST"] = "192.168.1.1"

        try:
            config = Config()
            assert config.get("HTTP_TCP_PORT") == 8082
            assert config.get("DATA_DIR") == "./data"
            assert config.get("HTTP_API_PORT") == 7000
            assert config.get("HOST") == "192.168.1.1"
        finally:
            for key in ["HTTP_API_PORT", "HOST"]:
                if key in os.environ:
                    del os.environ[key]

    def test_config_env_type_conversion(self):
        os.environ["HTTP_API_PORT"] = "not_a_number"
        os.environ["PERMISSION_CHECK"] = "not_a_boolean"

        try:
            config = Config()
            assert config.get("HTTP_API_PORT") == 8080
            assert config.get("PERMISSION_CHECK") is True
        finally:
            for key in ["HTTP_API_PORT", "PERMISSION_CHECK"]:
                if key in os.environ:
                    del os.environ[key]

    def test_config_get_with_default(self):
        config = Config()
        config.set("HTTP_API_PORT", 9000)
        assert config.get("HTTP_API_PORT") == 9000
        assert config.get("NONEXISTENT_KEY") is None

    def test_config_all(self):
        config = Config()
        assert isinstance(config.http_api_port, int)
        assert isinstance(config.http_tcp_port, int)
        assert isinstance(config.host, str)
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.store_dir, Path)
        assert isinstance(config.log_level, str)
        assert isinstance(config.permission_check, bool)
        assert config.http_api_port == 8080
        assert config.http_tcp_port == 8082
        assert config.host == "0.0.0.0"
        assert config.data_dir == Path("./data")
        assert config.store_dir == Path("./store")
        assert config.log_level == "INFO"
        assert config.permission_check is True


class TestGlobalConfig:
    def test_singleton(self):
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_init_config(self):
        config = init_config("/nonexistent/config.json")
        assert isinstance(config, Config)
        assert config is get_config()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
