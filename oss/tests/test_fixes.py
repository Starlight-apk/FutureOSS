Simple test to verify our fixes

import os
import tempfile
import pytest
from pathlib import Path

from oss.config import Config
from oss.logger.logger import Logger


def test_cors_fix():
    config = Config()
    
    assert config.get("LOG_FILE") == ""
    assert config.get("LOG_MAX_SIZE") == 10485760    assert config.get("LOG_BACKUP_COUNT") == 5
    
    os.environ["LOG_FILE"] = "/tmp/test.log"
    os.environ["LOG_MAX_SIZE"] = "20971520"    os.environ["LOG_BACKUP_COUNT"] = "10"
    
    config = Config()
    
    assert config.get("LOG_FILE") == "/tmp/test.log"
    assert config.get("LOG_MAX_SIZE") == 20971520
    assert config.get("LOG_BACKUP_COUNT") == 10
    
    for key in ["LOG_FILE", "LOG_MAX_SIZE", "LOG_BACKUP_COUNT"]:
        if key in os.environ:
            del os.environ[key]


def test_logger_functionality():
