Tests for HTTP API

import json
import pytest
from unittest.mock import Mock, patch

from oss.config import get_config
from oss.logger.logger import Log
from store.@{NebulaShell}.http-api.server import HttpServer, Request, Response
from store.@{NebulaShell}.http-api.middleware import MiddlewareChain, CorsMiddleware, AuthMiddleware, LoggerMiddleware


class TestRequest:
        req = Request("GET", "/test", {"Content-Type": "application/json"}, '{"test": true}')
        
        assert req.method == "GET"
        assert req.path == "/test"
        assert req.headers == {"Content-Type": "application/json"}
        assert req.body == '{"test": true}'
        assert req.path_params == {}


class TestResponse:
        resp = Response()
        
        assert resp.status == 200
        assert resp.headers == {}
        assert resp.body == ""
    
    def test_response_initialization_with_params(self):
    
    @pytest.fixture
    def mock_router(self):
        return MiddlewareChain()
    
    def test_http_server_initialization(self, mock_router, middleware_chain):
        server = HttpServer(mock_router, middleware_chain, host="127.0.0.1", port=9000)
        
        assert server.host == "127.0.0.1"
        assert server.port == 9000
    
    @patch('store.@{NebulaShell}.http-api.server.HTTPServer')
    def test_http_server_start(self, mock_http_server, mock_router, middleware_chain):
        server = HttpServer(mock_router, middleware_chain)
        
        mock_server_instance = Mock()
        server._server = mock_server_instance
        
        server.stop()
        
        mock_server_instance.shutdown.assert_called_once()


class TestMiddleware:
        from store.@{NebulaShell}.http-api.middleware import Middleware
        
        class TestMiddleware(Middleware):
            def process(self, ctx, next_fn):
                return next_fn()
        
        middleware = TestMiddleware()
        ctx = {}
        next_fn = Mock(return_value=None)
        
        result = middleware.process(ctx, next_fn)
        
        next_fn.assert_called_once()
        assert result is None
    
    def test_cors_middleware_process(self):
        middleware = AuthMiddleware()
        ctx = {"request": Request("GET", "/api/test", {}, "")}
        next_fn = Mock(return_value=None)
        
        with patch('store.@{NebulaShell}.http-api.middleware.get_config') as mock_get_config:
            mock_get_config.return_value.get.return_value = ""
            
            result = middleware.process(ctx, next_fn)
            
            next_fn.assert_called_once()
            assert result is None
    
    def test_auth_middleware_process_public_path(self):
        middleware = AuthMiddleware()
        ctx = {"request": Request("GET", "/api/test", {"Authorization": "Bearer test-key"}, "")}
        next_fn = Mock(return_value=None)
        
        with patch('store.@{NebulaShell}.http-api.middleware.get_config') as mock_get_config:
            mock_get_config.return_value.get.return_value = "test-key"
            
            result = middleware.process(ctx, next_fn)
            
            next_fn.assert_called_once()
            assert result is None
    
    def test_auth_middleware_process_with_invalid_token(self):
        middleware = LoggerMiddleware()
        ctx = {"request": Request("GET", "/api/test", {}, "")}
        next_fn = Mock(return_value=None)
        
        with patch.object(Log, 'info') as mock_log:
            result = middleware.process(ctx, next_fn)
            
            next_fn.assert_called_once()
            mock_log.assert_called_once_with("http-api", "GET /api/test")
            assert result is None
    
    def test_logger_middleware_process_silent_path(self):
    
    def test_middleware_chain_initialization(self):
        chain = MiddlewareChain()
        initial_count = len(chain.middlewares)
        
        mock_middleware = Mock()
        chain.add(mock_middleware)
        
        assert len(chain.middlewares) == initial_count + 1
        assert chain.middlewares[-1] is mock_middleware
    
    def test_middleware_chain_run(self):
        chain = MiddlewareChain()
        ctx = {}
        
        response = Response(status=401, body='{"error": "Unauthorized"}')
        chain.middlewares[0].process = Mock(return_value=response)
        
        result = chain.run(ctx)
        
        chain.middlewares[0].process.assert_called_once()
        for middleware in chain.middlewares[1:]:
            middleware.process.assert_not_called()
        
        assert result is response


if __name__ == '__main__':
    pytest.main([__file__, '-v'])