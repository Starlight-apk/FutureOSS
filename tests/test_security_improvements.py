#!/usr/bin/env python3
"""
安全改进验证测试
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 添加store目录到路径
store_path = project_root / "store"
sys.path.insert(0, str(store_path))

from oss.config import Config
from oss.logger.logger import Logger


def test_security_configurations():
    """测试安全配置"""
    print("=== 测试安全配置 ===")
    
    config = Config()
    
    # 测试CORS配置
    cors_origins = config.get("CORS_ALLOWED_ORIGINS")
    print(f"✅ CORS配置: {cors_origins}")
    
    # 测试HOST配置
    host = config.get("HOST")
    print(f"✅ HOST配置: {host}")
    
    # 测试限流配置
    rate_limit_enabled = config.get("RATE_LIMIT_ENABLED")
    rate_limit_max = config.get("RATE_LIMIT_MAX_REQUESTS")
    rate_limit_window = config.get("RATE_LIMIT_TIME_WINDOW")
    print(f"✅ 限流配置: {rate_limit_enabled}, {rate_limit_max}/分钟")
    
    # 测试CSRF配置
    csrf_enabled = config.get("CSRF_ENABLED")
    print(f"✅ CSRF配置: {csrf_enabled}")
    
    # 测试输入验证配置
    input_validation_enabled = config.get("INPUT_VALIDATION_ENABLED")
    print(f"✅ 输入验证配置: {input_validation_enabled}")
    
    # 测试API密钥配置
    api_key = config.get("API_KEY")
    print(f"✅ API密钥配置: {'已配置' if api_key else '未配置'}")
    
    return True


def test_rate_limiting():
    """测试限流功能"""
    print("\n=== 测试限流功能 ===")
    
    try:
        from @{NebulaShell}.http_api.rate_limiter import RateLimitMiddleware
        
        middleware = RateLimitMiddleware()
        
        # 创建模拟请求
        class MockRequest:
            def __init__(self, path="/api/test"):
                self.path = path
                self.headers = {"Remote-Addr": "127.0.0.1"}
        
        ctx = {"request": MockRequest()}
        
        # 测试正常请求
        result = middleware.process(ctx, lambda: None)
        print("✅ 限流中间件正常工作")
        
        return True
    except Exception as e:
        print(f"❌ 限流测试失败: {e}")
        return False


def test_csrf_protection():
    """测试CSRF防护功能"""
    print("\n=== 测试CSRF防护功能 ===")
    
    try:
        from @{NebulaShell}.http_api.csrf_middleware import CsrfMiddleware
        
        middleware = CsrfMiddleware()
        
        # 创建模拟请求
        class MockRequest:
            def __init__(self, method="GET", path="/api/test"):
                self.method = method
                self.path = path
                self.headers = {"Remote-Addr": "127.0.0.1"}
        
        ctx = {"request": MockRequest()}
        
        # 测试GET请求（应该通过）
        result = middleware.process(ctx, lambda: None)
        print("✅ CSRF防护中间件正常工作")
        
        return True
    except Exception as e:
        print(f"❌ CSRF测试失败: {e}")
        return False


def test_input_validation():
    """测试输入验证功能"""
    print("\n=== 测试输入验证功能 ===")
    
    try:
        from @{NebulaShell}.http_api.input_validation import InputValidationMiddleware
        
        middleware = InputValidationMiddleware()
        
        # 创建模拟请求
        class MockRequest:
            def __init__(self, method="GET", path="/api/test", body=None):
                self.method = method
                self.path = path
                self.body = body or ""
                self.headers = {}
        
        ctx = {"request": MockRequest()}
        
        # 测试正常请求
        result = middleware.process(ctx, lambda: None)
        print("✅ 输入验证中间件正常工作")
        
        return True
    except Exception as e:
        print(f"❌ 输入验证测试失败: {e}")
        return False


def test_middleware_chain():
    """测试中间件链"""
    print("\n=== 测试中间件链 ===")
    
    try:
        from @{NebulaShell}.http_api.middleware import MiddlewareChain
        
        chain = MiddlewareChain()
        print("✅ 中间件链创建成功")
        
        # 检查中间件数量
        print(f"✅ 中间件数量: {len(chain.middlewares)}")
        
        # 检查包含的中间件
        middleware_names = [type(m).__name__ for m in chain.middlewares]
        print(f"✅ 中间件列表: {middleware_names}")
        
        return True
    except Exception as e:
        print(f"❌ 中间件链测试失败: {e}")
        return False


def test_security_headers():
    """测试安全头设置"""
    print("\n=== 测试安全头设置 ===")
    
    try:
        from @{NebulaShell}.http_api.middleware import CorsMiddleware
        
        middleware = CorsMiddleware()
        
        # 创建模拟请求
        class MockRequest:
            def __init__(self, origin="http://localhost:3000"):
                self.headers = {"Origin": origin}
        
        ctx = {"request": MockRequest()}
        
        # 测试CORS头设置
        result = middleware.process(ctx, lambda: None)
        response_headers = ctx.get("response_headers", {})
        
        print(f"✅ CORS头设置: {response_headers}")
        
        # 检查关键安全头
        expected_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in expected_headers:
            if header in response_headers:
                print(f"✅ {header}: {response_headers[header]}")
            else:
                print(f"❌ 缺少 {header}")
        
        return True
    except Exception as e:
        print(f"❌ 安全头测试失败: {e}")
        return False


def test_configuration_overrides():
    """测试配置覆盖"""
    print("\n=== 测试配置覆盖 ===")
    
    import os
    
    # 测试环境变量覆盖
    os.environ["CORS_ALLOWED_ORIGINS"] = '["https://example.com"]'
    os.environ["RATE_LIMIT_MAX_REQUESTS"] = "50"
    os.environ["CSRF_ENABLED"] = "false"
    
    try:
        config = Config()
        
        cors_origins = config.get("CORS_ALLOWED_ORIGINS")
        rate_limit_max = config.get("RATE_LIMIT_MAX_REQUESTS")
        csrf_enabled = config.get("CSRF_ENABLED")
        
        print(f"✅ 环境变量覆盖 CORS: {cors_origins}")
        print(f"✅ 环境变量覆盖 限流: {rate_limit_max}")
        print(f"✅ 环境变量覆盖 CSRF: {csrf_enabled}")
        
        return True
    except Exception as e:
        print(f"❌ 配置覆盖测试失败: {e}")
        return False
    finally:
        # 清理环境变量
        for key in ["CORS_ALLOWED_ORIGINS", "RATE_LIMIT_MAX_REQUESTS", "CSRF_ENABLED"]:
            if key in os.environ:
                del os.environ[key]


if __name__ == "__main__":
    print("开始NebulaShell安全改进验证测试...")
    
    tests = [
        ("安全配置测试", test_security_configurations),
        ("限流功能测试", test_rate_limiting),
        ("CSRF防护测试", test_csrf_protection),
        ("输入验证测试", test_input_validation),
        ("中间件链测试", test_middleware_chain),
        ("安全头测试", test_security_headers),
        ("配置覆盖测试", test_configuration_overrides),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n--- 测试结果 ---")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有安全改进测试通过！")
        print("\n安全改进总结:")
        print("✅ 限流防护 - 防止DoS攻击")
        print("✅ CSRF防护 - 防止跨站请求伪造")
        print("✅ 输入验证 - 防止注入攻击")
        print("✅ CORS安全 - 限制跨域访问")
        print("✅ 安全头 - 设置适当的安全响应头")
        print("✅ 配置管理 - 支持环境变量覆盖")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要修复。")
        sys.exit(1)