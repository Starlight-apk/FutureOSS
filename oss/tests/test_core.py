"""核心模块测试套件"""
import pytest
from oss.core.context import Context
from oss.plugin.types import Response, Metadata, PluginConfig, Manifest
from oss.plugin.loader import PluginLoader
from oss.shared.router import BaseRouter, match_path, extract_path_params


class TestContext:
    """测试 Context 类"""
    
    def test_context_initialization(self):
        """测试 Context 初始化"""
        ctx = Context()
        assert ctx.config == {}
        assert ctx._state == {}
    
    def test_context_with_config(self):
        """测试带配置的 Context"""
        config = {"key": "value", "number": 42}
        ctx = Context(config)
        assert ctx.config == config
        assert ctx.get("key") == "value"
        assert ctx.get("number") == 42
        assert ctx.get("missing", "default") == "default"
    
    def test_context_state_management(self):
        """测试状态管理"""
        ctx = Context()
        ctx.set_state("user_id", 123)
        ctx.set_state("session", "abc")
        
        assert ctx.get_state("user_id") == 123
        assert ctx.get_state("session") == "abc"
        assert ctx.get_state("missing", "default") == "default"
    
    def test_context_repr(self):
        """测试字符串表示"""
        ctx = Context({"test": "value"})
        repr_str = repr(ctx)
        assert "Context" in repr_str
        assert "test" in repr_str


class TestPluginTypes:
    """测试插件类型"""
    
    def test_response_creation(self):
        """测试 Response 创建"""
        resp = Response(status=200, headers={"Content-Type": "application/json"}, body="OK")
        assert resp.status == 200
        assert resp.headers["Content-Type"] == "application/json"
        assert resp.body == "OK"
    
    def test_response_defaults(self):
        """测试 Response 默认值"""
        resp = Response()
        assert resp.status == 200
        assert resp.headers == {}
        assert resp.body == ""
    
    def test_metadata_creation(self):
        """测试 Metadata 创建"""
        meta = Metadata(name="test-plugin", version="1.0.0", author="Test", description="A test plugin")
        assert meta.name == "test-plugin"
        assert meta.version == "1.0.0"
        assert meta.author == "Test"
        assert meta.description == "A test plugin"
    
    def test_plugin_config_creation(self):
        """测试 PluginConfig 创建"""
        config = PluginConfig(enabled=True, args={"key": "value"})
        assert config.enabled is True
        assert config.args["key"] == "value"
    
    def test_manifest_creation(self):
        """测试 Manifest 创建"""
        manifest = Manifest()
        assert isinstance(manifest.metadata, Metadata)
        assert isinstance(manifest.config, PluginConfig)
        assert manifest.dependencies == []


class TestRouter:
    """测试路由功能"""
    
    def test_exact_match(self):
        """测试精确匹配"""
        assert match_path("/api/users", "/api/users") is True
        assert match_path("/api/users", "/api/posts") is False
    
    def test_param_match(self):
        """测试参数匹配"""
        assert match_path("/api/users/:id", "/api/users/123") is True
        assert match_path("/api/users/:id", "/api/users/123/profile") is False
    
    def test_wildcard_match(self):
        """测试通配符匹配"""
        assert match_path("/api/:path", "/api/users/123/profile") is True
        assert match_path("/api/:wildcard", "/api/a/b/c") is True
    
    def test_extract_params(self):
        """测试参数提取"""
        params = extract_path_params("/api/users/:id", "/api/users/123")
        assert params == {"id": "123"}
        
        params = extract_path_params("/api/:version/:resource", "/api/v1/users")
        assert params == {"version": "v1", "resource": "users"}
    
    def test_extract_wildcard_params(self):
        """测试通配符参数提取"""
        params = extract_path_params("/api/:path", "/api/users/123/profile")
        assert params == {"path": "users/123/profile"}


class TestBaseRouter:
    """测试 BaseRouter 类"""
    
    def test_add_routes(self):
        """测试添加路由"""
        router = BaseRouter()
        
        def handler(req):
            pass
        
        router.get("/users", handler)
        router.post("/users", handler)
        router.put("/users/:id", handler)
        router.delete("/users/:id", handler)
        
        assert len(router.routes) == 4
    
    def test_find_route(self):
        """测试查找路由"""
        router = BaseRouter()
        
        def handler(req):
            return "response"
        
        router.get("/users/:id", handler)
        
        route, params = router.find_route("GET", "/users/123")
        assert route is not None
        assert route.handler == handler
        assert params == {"id": "123"}
    
    def test_find_route_not_found(self):
        """测试未找到路由"""
        router = BaseRouter()
        
        def handler(req):
            return "response"
        
        router.get("/users", handler)
        
        result = router.find_route("GET", "/posts")
        assert result is None
        
        result = router.find_route("POST", "/users")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

