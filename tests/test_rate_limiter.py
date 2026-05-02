#!/usr/bin/env python3
"""
限流功能测试
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

# 动态导入
import importlib.util
import sys

def dynamic_import(module_path, class_name):
    spec = importlib.util.spec_from_file_location("module", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["module"] = module
    spec.loader.exec_module(module)
    return getattr(module, class_name)

# 获取限流器类
rate_limiter_path = str(project_root / "store" / "NebulaShell" / "http-api" / "rate_limiter.py")
RateLimiter = dynamic_import(rate_limiter_path, "RateLimiter")
RateLimitMiddleware = dynamic_import(rate_limiter_path, "RateLimitMiddleware")


def test_rate_limiter():
    """测试限流器基本功能"""
    print("=== 测试限流器 ===")
    
    # 创建限流器
    limiter = RateLimiter(max_requests=3, time_window=1)
    
    # 测试正常请求
    for i in range(3):
        allowed = limiter.is_allowed("test_ip")
        print(f"请求 {i+1}: {'允许' if allowed else '拒绝'}")
        assert allowed, f"请求 {i+1} 应该被允许"
    
    # 测试超出限制
    allowed = limiter.is_allowed("test_ip")
    print(f"请求 4: {'允许' if allowed else '拒绝'}")
    assert not allowed, "请求 4 应该被拒绝"
    
    print("✅ 限流器基本功能测试通过")


def test_rate_limit_middleware():
    """测试限流中间件"""
    print("\n=== 测试限流中间件 ===")
    
    # 创建中间件
    middleware = RateLimitMiddleware()
    
    # 创建模拟请求
    class MockRequest:
        def __init__(self, path="/api/test", headers=None):
            self.path = path
            self.headers = headers or {"Remote-Addr": "127.0.0.1"}
    
    # 测试禁用限流
    middleware.enabled = False
    ctx = {"request": MockRequest()}
    result = middleware.process(ctx, lambda: None)
    assert result is None, "禁用限流时应该直接通过"
    print("✅ 禁用限流测试通过")
    
    # 测试启用限流
    middleware.enabled = True
    ctx = {"request": MockRequest()}
    result = middleware.process(ctx, lambda: None)
    assert result is None, "启用限流时应该允许请求"
    print("✅ 启用限流测试通过")
    
    print("✅ 限流中间件测试通过")


def test_endpoint_specific_limiting():
    """测试端点特定限流"""
    print("\n=== 测试端点特定限流 ===")
    
    # 创建中间件
    middleware = RateLimitMiddleware()
    
    # 测试不同端点的限流配置
    class MockRequest:
        def __init__(self, path, headers=None):
            self.path = path
            self.headers = headers or {"Remote-Addr": "127.0.0.1"}
    
    # 测试普通端点
    ctx = {"request": MockRequest("/api/test")}
    result = middleware.process(ctx, lambda: None)
    assert result is None, "普通端点应该允许请求"
    print("✅ 普通端点限流测试通过")
    
    # 测试特定端点
    ctx = {"request": MockRequest("/api/dashboard/stats")}
    result = middleware.process(ctx, lambda: None)
    assert result is None, "特定端点应该允许请求"
    print("✅ 特定端点限流测试通过")
    
    print("✅ 端点特定限流测试通过")


def test_client_identification():
    """测试客户端标识符"""
    print("\n=== 测试客户端标识符 ===")
    
    middleware = RateLimitMiddleware()
    
    # 测试IP标识符
    request = type('Request', (), {
        'headers': {'Remote-Addr': '192.168.1.1'}
    })()
    identifier = middleware.get_client_identifier(request)
    assert identifier == "ip:192.168.1.1", f"IP标识符错误: {identifier}"
    print("✅ IP标识符测试通过")
    
    # 测试API Key标识符
    request = type('Request', (), {
        'headers': {'Authorization': 'Bearer test_key_123'}
    })()
    identifier = middleware.get_client_identifier(request)
    assert identifier == "api_key:test_key_123", f"API Key标识符错误: {identifier}"
    print("✅ API Key标识符测试通过")
    
    print("✅ 客户端标识符测试通过")


def test_rate_limit_response():
    """测试限流响应"""
    print("\n=== 测试限流响应 ===")
    
    middleware = RateLimitMiddleware()
    response = middleware.create_rate_limit_response()
    
    assert response.status == 429, f"状态码错误: {response.status}"
    assert "Rate limit exceeded" in response.body, "响应体错误"
    assert "Retry-After" in response.headers, "缺少Retry-After头"
    assert "X-Rate-Limit-Limit" in response.headers, "缺少X-Rate-Limit-Limit头"
    
    print("✅ 限流响应测试通过")


if __name__ == "__main__":
    print("开始限流功能测试...")
    
    tests = [
        ("限流器基本功能测试", test_rate_limiter),
        ("限流中间件测试", test_rate_limit_middleware),
        ("端点特定限流测试", test_endpoint_specific_limiting),
        ("客户端标识符测试", test_client_identification),
        ("限流响应测试", test_rate_limit_response),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            test_func()
            passed += 1
            print(f"✅ {test_name} 通过")
        except Exception as e:
            print(f"❌ {test_name} 失败: {e}")
    
    print(f"\n--- 测试结果 ---")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有限流功能测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要修复。")
        sys.exit(1)