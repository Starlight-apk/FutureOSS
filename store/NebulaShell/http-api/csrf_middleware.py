"""
CSRF 防护中间件
"""
import hashlib
import secrets
import time
from typing import Dict, Optional
from collections import defaultdict

from oss.config import get_config
from oss.logger.logger import Log
from .server import Request, Response


class CsrfTokenManager:
    """CSRF 令牌管理器"""
    
    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.get("CSRF_ENABLED", True)
        self.token_lifetime = self.config.get("CSRF_TOKEN_LIFETIME", 3600)  # 1小时
        self.tokens: Dict[str, tuple] = {}  # {token: (timestamp, session_id)}
        self.session_tokens: Dict[str, str] = defaultdict(str)  # {session_id: token}
        self.lock = None  # 延迟初始化
    
    def _init_lock(self):
        """延迟初始化锁"""
        if self.lock is None:
            import threading
            self.lock = threading.Lock()
    
    def generate_token(self, session_id: str) -> str:
        """生成CSRF令牌"""
        if not self.enabled:
            return None
        
        self._init_lock()
        
        # 如果已有令牌，直接返回
        if session_id in self.session_tokens:
            return self.session_tokens[session_id]
        
        # 生成新的令牌
        token = secrets.token_urlsafe(32)
        timestamp = time.time()
        
        # 存储令牌
        self.tokens[token] = (timestamp, session_id)
        self.session_tokens[session_id] = token
        
        return token
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """验证CSRF令牌"""
        if not self.enabled:
            return True
        
        self._init_lock()
        
        # 清理过期令牌
        current_time = time.time()
        expired_tokens = []
        
        for stored_token, (timestamp, stored_session_id) in self.tokens.items():
            if current_time - timestamp > self.token_lifetime:
                expired_tokens.append(stored_token)
            elif stored_session_id == session_id and stored_token == token:
                # 令牌有效，更新时间戳
                self.tokens[stored_token] = (current_time, stored_session_id)
                return True
        
        # 清理过期令牌
        for expired_token in expired_tokens:
            if expired_token in self.tokens:
                del self.tokens[expired_token]
        
        return False
    
    def cleanup_expired_tokens(self):
        """清理过期令牌"""
        if not self.enabled:
            return
        
        self._init_lock()
        
        current_time = time.time()
        expired_tokens = []
        
        for token, (timestamp, _) in self.tokens.items():
            if current_time - timestamp > self.token_lifetime:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            if token in self.tokens:
                del self.tokens[token]


class CsrfMiddleware:
    """CSRF 防护中间件"""
    
    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.get("CSRF_ENABLED", True)
        self.exempt_paths = {
            "/health", "/favicon.ico", "/api/status", 
            "/api/health", "/login", "/logout"
        }
        
        # 初始化令牌管理器
        self.token_manager = CsrfTokenManager()
    
    def get_session_id(self, request: Request) -> str:
        """获取会话ID"""
        # 从Cookie中获取会话ID
        session_cookie = request.headers.get("Cookie", "")
        for cookie in session_cookie.split(";"):
            if "session_id" in cookie:
                return cookie.split("=")[1].strip()
        
        # 从Authorization头获取（如果使用Bearer token）
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return f"token:{auth_header[7:]}"
        
        # 使用IP地址作为会话ID（简化实现）
        return f"ip:{request.headers.get('Remote-Addr', 'unknown')}"
    
    def create_csrf_token_response(self, session_id: str) -> Response:
        """创建CSRF令牌响应"""
        token = self.token_manager.generate_token(session_id)
        
        return Response(
            status=200,
            headers={
                "Content-Type": "application/json",
                "Set-Cookie": f"csrf_token={token}; Path=/; HttpOnly; SameSite=Lax"
            },
            body=json.dumps({
                "csrf_token": token,
                "message": "CSRF token generated"
            })
        )
    
    def process(self, ctx: dict, next_fn) -> Optional[Response]:
        """处理CSRF防护逻辑"""
        if not self.enabled:
            return next_fn()
        
        request = ctx.get("request")
        if not request:
            return next_fn()
        
        # 检查是否为豁免路径
        if request.path in self.exempt_paths:
            return next_fn()
        
        # 只对需要保护的请求方法进行CSRF检查
        if request.method not in ["POST", "PUT", "DELETE", "PATCH"]:
            return next_fn()
        
        # 获取会话ID
        session_id = self.get_session_id(request)
        
        # 获取CSRF令牌
        csrf_token = None
        if request.headers.get("Content-Type") == "application/json":
            try:
                import json
                body = json.loads(request.body)
                csrf_token = body.get("csrf_token")
            except:
                pass
        
        # 从Header中获取CSRF令牌
        if not csrf_token:
            csrf_token = request.headers.get("X-CSRF-Token")
        
        # 验证CSRF令牌
        if not csrf_token or not self.token_manager.validate_token(csrf_token, session_id):
            Log.warn("csrf", f"CSRF验证失败: {request.method} {request.path}")
            return Response(
                status=403,
                body='{"error": "CSRF token invalid or missing", "message": "请求被拒绝，请刷新页面重试"}',
                headers={"Content-Type": "application/json"}
            )
        
        return next_fn()