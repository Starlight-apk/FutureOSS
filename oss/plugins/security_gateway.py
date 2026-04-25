"""
FutureOSS v1.1.0 - 统一安全网关与审计中心
功能：API 限流、IP 黑白名单、JWT 认证、操作审计、异常行为检测
"""
import time
import logging
import jwt
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from oss.plugin.base import BasePlugin
from oss.core.context import Context

logger = logging.getLogger("futureoss.security")

class SecurityGatewayPlugin(BasePlugin):
    name = "security_gateway"
    version = "1.1.0"
    description = "统一安全网关：限流、鉴权、审计、熔断"
    
    def __init__(self):
        super().__init__()
        self.rate_limit_store: Dict[str, List[float]] = defaultdict(list)
        self.ip_blacklist: set = set()
        self.ip_whitelist: set = set()
        self.secret_key = "futureoss_secret_key_v1.1.0_change_in_prod"
        self.audit_logs: List[Dict] = []
        self.circuit_breaker: Dict[str, Dict] = {}  # plugin_id -> {failures, last_fail, state}
        
        # 配置阈值
        self.rate_limit_reqs = 100  # 每秒请求数
        self.circuit_breaker_threshold = 5  # 失败次数阈值
        self.circuit_breaker_timeout = 60  # 熔断恢复时间 (秒)

    def on_load(self, ctx: Context):
        logger.info("安全网关已启动")
        # 注册中间件
        ctx.register_middleware("pre_request", self.pre_request_filter)
        ctx.register_middleware("post_action", self.audit_action)
        
        # 注册管理命令
        ctx.register_command("security.add_blacklist", self.add_blacklist)
        ctx.register_command("security.audit.query", self.query_audit_logs)
        ctx.register_command("security.circuit.reset", self.reset_circuit)

    def pre_request_filter(self, request: Dict, client_ip: str) -> bool:
        """请求前置过滤：限流、黑白名单、鉴权"""
        now = time.time()
        
        # 1. 白名单跳过检查
        if client_ip in self.ip_whitelist:
            return True
            
        # 2. 黑名单拦截
        if client_ip in self.ip_blacklist:
            logger.warning(f"IP {client_ip} 在黑名单中，拒绝访问")
            return False
            
        # 3. 限流检查 (滑动窗口)
        user_requests = self.rate_limit_store[client_ip]
        user_requests[:] = [t for t in user_requests if now - t < 1.0]
        
        if len(user_requests) >= self.rate_limit_reqs:
            logger.warning(f"IP {client_ip} 触发限流")
            self.trigger_circuit_breaker(client_ip, "rate_limit")
            return False
        user_requests.append(now)
        
        # 4. JWT 鉴权 (针对受保护资源)
        if request.get("path", "").startswith("/admin"):
            token = request.get("headers", {}).get("Authorization", "")
            if not self.validate_jwt(token):
                logger.warning(f"IP {client_ip} 鉴权失败")
                return False
                
        return True

    def audit_action(self, action: str, user: str, details: Dict):
        """记录操作审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "details": details,
            "hash": hashlib.sha256(f"{action}{user}{time.time()}".encode()).hexdigest()[:8]
        }
        self.audit_logs.append(log_entry)
        # 保留最近 1000 条
        if len(self.audit_logs) > 1000:
            self.audit_logs.pop(0)
        logger.info(f"AUDIT: {action} by {user}")

    def trigger_circuit_breaker(self, target: str, reason: str):
        """触发熔断机制"""
        if target not in self.circuit_breaker:
            self.circuit_breaker[target] = {"failures": 0, "last_fail": 0, "state": "closed"}
        
        cb = self.circuit_breaker[target]
        cb["failures"] += 1
        cb["last_fail"] = time.time()
        
        if cb["failures"] >= self.circuit_breaker_threshold:
            cb["state"] = "open"
            logger.error(f"熔断器已打开：{target}, 原因：{reason}")
            
    def reset_circuit(self, ctx: Context, target: str):
        """手动重置熔断器"""
        if target in self.circuit_breaker:
            self.circuit_breaker[target] = {"failures": 0, "last_fail": 0, "state": "closed"}
            return {"status": "success", "message": f"熔断器 {target} 已重置"}
        return {"status": "error", "message": "目标不存在"}

    def validate_jwt(self, token: str) -> bool:
        try:
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return True
        except:
            return False

    def add_blacklist(self, ctx: Context, ip: str):
        self.ip_blacklist.add(ip)
        return {"status": "success", "message": f"IP {ip} 已加入黑名单"}

    def query_audit_logs(self, ctx: Context, limit: int = 10):
        return self.audit_logs[-limit:]

    def on_unload(self, ctx: Context):
        logger.info("安全网关已停止")
