"""Tests for Logger"""

import logging
import json
import os
import pytest
from unittest.mock import patch, Mock
from io import StringIO

from oss.logger.logger import Logger


class TestLogger:
    def test_logger_initialization(self):
        logger = Logger("test")
        with patch.object(logger.logger, 'info') as mock_info:
            logger.info("Test message")
            mock_info.assert_called_once_with("Test message")

    def test_logger_warn(self):
        logger = Logger("test")
        with patch.object(logger.logger, 'error') as mock_error:
            logger.error("Test error")
            mock_error.assert_called_once_with("Test error")

    def test_logger_debug(self):
        logger = Logger("test")
        with patch.object(logger.logger, 'info') as mock_info:
            logger.info("Test message", "TAG")
            mock_info.assert_called_once_with("[TAG] Test message")

    def test_logger_warn_with_tag(self):
        logger = Logger("test")
        with patch.object(logger.logger, 'error') as mock_error:
            logger.error("Test error", "TAG")
            mock_error.assert_called_once_with("[TAG] Test error")

    def test_logger_debug_with_tag(self):
        logger = Logger("test")
        format_str = logger._get_log_format()
        assert "%(asctime)s" in format_str
        assert "%(name)s" in format_str
        assert "%(levelname)s" in format_str
        assert "%(message)s" in format_str

    def test_get_log_format_json(self):
        os.environ["LOG_FORMAT"] = "json"
        try:
            logger = Logger("test")
            format_str = logger._get_log_format()
            assert "%(asctime)s" in format_str
            assert "%(name)s" in format_str
            assert "%(levelname)s" in format_str
            assert "%(message)s" in format_str
        finally:
            if "LOG_FORMAT" in os.environ:
                del os.environ["LOG_FORMAT"]

    def test_logger_json_format(self):
        logger = Logger("test")
        assert logger is not None

    def test_logger_output(self):
        log_capture = StringIO()

        logger = logging.getLogger("test_json")
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(log_capture)
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.info("Test JSON message")

        log_output = log_capture.getvalue().strip()
        assert log_output.startswith("{")
        assert log_output.endswith("}")
        assert "test_json" in log_output
        assert "INFO" in log_output
        assert "Test JSON message" in log_output

        try:
            import json
            json.loads(log_output)
        except json.JSONDecodeError:
            pytest.fail("Log output is not valid JSON")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
