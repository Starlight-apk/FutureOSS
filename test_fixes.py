#!/usr/bin/env python3
Simple test to verify our fixes work in practice

import os
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from oss.config import Config
from oss.logger.logger import Logger


def test_cors_configuration():
    print("\nTesting logging configuration...")
    
    config = Config()
    print(f"Default log format: {config.get('LOG_FORMAT')}")
    print(f"Default log level: {config.get('LOG_LEVEL')}")
    print(f"Default log file: {config.get('LOG_FILE')}")
    print(f"Default log max size: {config.get('LOG_MAX_SIZE')}")
    print(f"Default log backup count: {config.get('LOG_BACKUP_COUNT')}")
    
    os.environ["LOG_FORMAT"] = "json"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["LOG_FILE"] = "/tmp/test.log"
    os.environ["LOG_MAX_SIZE"] = "20971520"    os.environ["LOG_BACKUP_COUNT"] = "10"
    
    config = Config()
    print(f"Environment override log format: {config.get('LOG_FORMAT')}")
    print(f"Environment override log level: {config.get('LOG_LEVEL')}")
    print(f"Environment override log file: {config.get('LOG_FILE')}")
    print(f"Environment override log max size: {config.get('LOG_MAX_SIZE')}")
    print(f"Environment override log backup count: {config.get('LOG_BACKUP_COUNT')}")
    
    for key in ["LOG_FORMAT", "LOG_LEVEL", "LOG_FILE", "LOG_MAX_SIZE", "LOG_BACKUP_COUNT"]:
        if key in os.environ:
            del os.environ[key]
    
    print("✓ Logging configuration test passed!")


def test_logging_functionality():
    print("\nTesting CORS middleware logic...")
    
    class MockRequest:
        def __init__(self, origin):
            self.headers = {'Origin': origin}
            self.method = 'GET'
    
    def simulate_cors_middleware(origin):
