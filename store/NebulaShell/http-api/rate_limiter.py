"""
限流中间件 - 防止DoS攻击
"""
import time
import threading
from typing import Dict, Optional
from collections import defaultdict, deque

from oss.config import get_config
from store.NebulaShell.http_api.server import Response


class RateLimiter:
    """令牌桶限流器"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        with self.lock:
            now = time.time()
            request_times = self.requests[identifier]
            
            # 清理过期的请求记录
            while request_times and request_times[0] <= now - self.time_window:
                request_times.popleft()
            
            # 检查是否超过限制
            if len(request_times) >= self.max_requests:
                return False
            
            # 记录当前请求
            request_times.append(now)
            return True


class RateLimitMiddleware:
    """限流中间件"""
    
    def __init__(self):
        self.config = get_config()
        self.limiter = RateLimiter(
            max_requests=self.config.get("RATE_LIMIT_MAX_REQUESTS", 100),
            time_window=self.config.get("RATE_LIMIT_TIME_WINDOW", 60)
        )
        self.enabled = self.config.get("RATE_LIMIT_ENABLED", True)
        
        # 不同端点的限流配置
        self.endpoint_limits = {
            "/api/dashboard/stats": {
                "max_requests": 10,
                "time_window": 60
            },
            "/api/pkg-manager/search": {
                "max_requests": 50,
                "time_window": 60
            }
        }
    
    def get_client_identifier(self, request) -> str:
        """获取客户端标识符"""
        # 优先使用IP地址
        ip = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", ""))
        if not ip:
            ip = request.headers.get("Remote-Addr", "unknown")
        
        # 如果有API Key，使用Key作为标识符（更精确）
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return f"api_key:{auth_header[7:]}"
        
        return f"ip:{ip}"
    
    def get_endpoint_limiter(self, path: str) -> Optional[RateLimiter]:
        """获取端点特定的限流器"""
        for endpoint, config in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return RateLimiter(
                    max_requests=config["max_requests"],
                    time_window=config["time_window"]
                )
        return None
    
    def create_rate_limit_response(self, retry_after: int = 60) -> Response:
        """创建限流响应"""
        return Response(
            status=429,
            headers={
                "Content-Type": "application/json",
                "Retry-After": str(retry_after),
                "X-Rate-Limit-Limit": str(self.limiter.max_requests),
                "X-Rate-Limit-Window": str(self.limiter.time_window),
            },
            body='{"error": "Rate limit exceeded", "message": "请稍后再试"}'
        )
    
    def process(self, ctx: dict, next_fn) -> Optional[Response]:
        """处理限流逻辑"""
        if not self.enabled:
            return next_fn()
        
        request = ctx.get("request")
        if not request:
            return next_fn()
        
        # 获取客户端标识符
        identifier = self.get_client_identifier(request)
        
        # 获取端点特定的限流器
        endpoint_limiter = self.get_endpoint_limiter(request.path)
        limiter = endpoint_limiter or self.limiter
        
        # 检查是否允许请求
        if not limiter.is_allowed(identifier):
            retry_after = self.limiter.time_window
            return self.create_rate_limit_response(retry_after)
        
        return next_fn()