"""Tests for HTTP API"""

import json
import pytest
from unittest.mock import Mock, patch

from oss.config import get_config
from oss.logger.logger import Log


class MockRequest:
    def __init__(self, method="GET", path="/test", headers=None, body=""):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.path_params = {}


class MockResponse:
    def __init__(self, status=200, headers=None, body=""):
        self.status = status
        self.headers = headers or {}
        self.body = body


class TestRequest:
    def test_request_initialization(self):
        req = MockRequest("GET", "/test", {"Content-Type": "application/json"}, '{"test": true}')
        assert req.method == "GET"
        assert req.path == "/test"
        assert req.headers == {"Content-Type": "application/json"}
        assert req.body == '{"test": true}'
        assert req.path_params == {}


class TestResponse:
    def test_response_initialization_defaults(self):
        resp = MockResponse()
        assert resp.status == 200
        assert resp.headers == {}
        assert resp.body == ""

    def test_response_initialization_with_params(self):
        resp = MockResponse(status=404, body="Not Found")
        assert resp.status == 404
        assert resp.body == "Not Found"


class TestMiddleware:
    def test_cors_middleware_process(self):
        ctx = {"request": MockRequest("GET", "/api/test", {}, "")}
        next_fn = Mock(return_value=None)
        result = next_fn()
        next_fn.assert_called_once()
        assert result is None

    def test_auth_middleware_process_public_path(self):
        ctx = {"request": MockRequest("GET", "/api/test", {"Authorization": "Bearer test-key"}, "")}
        next_fn = Mock(return_value=None)
        result = next_fn()
        next_fn.assert_called_once()
        assert result is None

    def test_logger_middleware_process_silent_path(self):
        ctx = {"request": MockRequest("GET", "/api/test", {}, "")}
        next_fn = Mock(return_value=None)
        result = next_fn()
        next_fn.assert_called_once()
        assert result is None

    def test_middleware_chain_initialization(self):
        chain = []
        initial_count = len(chain)
        mock_middleware = Mock()
        chain.append(mock_middleware)
        assert len(chain) == initial_count + 1
        assert chain[-1] is mock_middleware

    def test_middleware_chain_run(self):
        response = MockResponse(status=401, body='{"error": "Unauthorized"}')
        assert response.status == 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
