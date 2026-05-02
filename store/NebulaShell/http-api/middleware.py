"""中间件链 - CORS/鉴权/日志/限流/CSRF/输入验证等"""
import json
import time
from typing import Callable, Optional, Any

from oss.config import get_config
from oss.logger.logger import Log
from .server import Request, Response
from .rate_limiter import RateLimitMiddleware
from .csrf_middleware import CsrfMiddleware
from .input_validation import InputValidationMiddleware


class Middleware:
    """中间件基类"""
    def process(self, ctx: dict[str, Any], next_fn: Callable) -> Optional[Response]:
        return next_fn()


class CorsMiddleware(Middleware):
    """CORS 中间件"""
    def process(self, ctx: dict, next_fn: Callable) -> Optional[Response]:
        config = get_config()
        allowed_origins = config.get("CORS_ALLOWED_ORIGINS", ["http://localhost:3000", "http://127.0.0.1:3000"])
        
        req = ctx.get("request")
        origin = req.headers.get("Origin", "") if req else ""
        
        # 如果没有配置允许的来源或来源为空，则不设置CORS头
        if not allowed_origins or not origin:
            return next_fn()
            
        # 检查请求来源是否在允许列表中
        if origin in allowed_origins or "*" in allowed_origins:
            ctx["response_headers"] = {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Access-Control-Allow-Credentials": "true",
            }
        
        return next_fn()


class AuthMiddleware(Middleware):
    """鉴权中间件 - Bearer Token 认证"""
    _public_paths = {"/health", "/favicon.ico", "/api/status", "/api/health"}
    
    def process(self, ctx: dict, next_fn: Callable) -> Optional[Response]:
        config = get_config()
        api_key = config.get("API_KEY")

        if not api_key:
            return next_fn()

        req = ctx.get("request")
        if req and req.path in self._public_paths:
            return next_fn()

        if req and req.method == "OPTIONS":
            return next_fn()

        auth_header = req.headers.get("Authorization", "") if req else ""
        token = auth_header.removeprefix("Bearer ").strip()

        if token != api_key or not token:
            Log.warn("auth", f"鉴权失败: {req.method} {req.path}" if req else "鉴权失败")
            return Response(
                status=401,
                body=json.dumps({"error": "Unauthorized", "message": "需要有效的 API Key"}),
                headers={"Content-Type": "application/json"},
            )
        return next_fn()


class LoggerMiddleware(Middleware):
    """日志中间件"""
    _silent_paths = {"/api/dashboard/stats", "/favicon.ico", "/health"}

    def process(self, ctx: dict, next_fn: Callable) -> Optional[Response]:
        req = ctx.get("request")
        if req and req.path not in self._silent_paths:
            Log.info("http-api", f"{req.method} {req.path}")
        return next_fn()


class RateLimitMiddleware(Middleware):
    """限流中间件 - 防止DoS攻击"""
    def __init__(self):
        self.config = get_config()
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
        
        # 全局限流配置
        self.global_limit = {
            "max_requests": self.config.get("RATE_LIMIT_MAX_REQUESTS", 100),
            "time_window": self.config.get("RATE_LIMIT_TIME_WINDOW", 60)
        }
        
        # 请求记录
        self.requests = {}
        self.lock = None  # 延迟初始化
    
    def _init_lock(self):
        """延迟初始化锁"""
        if self.lock is None:
            import threading
            self.lock = threading.Lock()
    
    def _get_client_identifier(self, request: Request) -> str:
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
    
    def _is_rate_limited(self, identifier: str, path: str) -> bool:
        """检查是否被限流"""
        if not self.enabled:
            return False
        
        now = time.time()
        limit_key = f"{identifier}:{path}"
        
        # 获取端点特定的限制
        endpoint_limit = None
        for endpoint, config in self.endpoint_limits.items():
            if path.startswith(endpoint):
                endpoint_limit = config
                break
        
        # 使用端点特定限制或全局限制
        limit = endpoint_limit or self.global_limit
        max_requests = limit["max_requests"]
        time_window = limit["time_window"]
        
        # 清理过期的请求记录
        if limit_key not in self.requests:
            self.requests[limit_key] = []
        
        request_times = self.requests[limit_key]
        while request_times and request_times[0] <= now - time_window:
            request_times.popleft()
        
        # 检查是否超过限制
        if len(request_times) >= max_requests:
            return True
        
        # 记录当前请求
        request_times.append(now)
        return False
    
    def _create_rate_limit_response(self) -> Response:
        """创建限流响应"""
        return Response(
            status=429,
            headers={
                "Content-Type": "application/json",
                "Retry-After": str(self.global_limit["time_window"]),
                "X-Rate-Limit-Limit": str(self.global_limit["max_requests"]),
                "X-Rate-Limit-Window": str(self.global_limit["time_window"]),
            },
            body='{"error": "Rate limit exceeded", "message": "请稍后再试"}'
        )
    
    def process(self, ctx: dict, next_fn: Callable) -> Optional[Response]:
        """处理限流逻辑"""
        if not self.enabled:
            return next_fn()
        
        request = ctx.get("request")
        if not request:
            return next_fn()
        
        # 获取客户端标识符
        self._init_lock()
        identifier = self._get_client_identifier(request)
        
        # 检查是否被限流
        if self._is_rate_limited(identifier, request.path):
            return self._create_rate_limit_response()
        
        return next_fn()


class MiddlewareChain:
    """中间件链"""

    def __init__(self):
        self.middlewares: list[Middleware] = []
        self.add(CorsMiddleware())
        self.add(AuthMiddleware())
        self.add(LoggerMiddleware())
        self.add(RateLimitMiddleware())
        self.add(CsrfMiddleware())
        self.add(InputValidationMiddleware())

    def add(self, middleware: Middleware):
        self.middlewares.append(middleware)

    def run(self, ctx: dict[str, Any]) -> Optional[Response]:
        idx = 0

        def next_fn():
            nonlocal idx
            if idx < len(self.middlewares):
                mw = self.middlewares[idx]
                idx += 1
                return mw.process(ctx, next_fn)
            return None

        resp = next_fn()
        response_headers = ctx.get("response_headers")
        if response_headers:
            ctx["_cors_headers"] = response_headers
        return resp