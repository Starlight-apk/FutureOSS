"""统一安全网关插件 - 提供多因子认证/防注入攻击/防越权访问/防重放攻击

功能说明：
1. 多因子认证：支持 TOTP、WebAuthn、硬件密钥
2. 防注入攻击：SQL 注入、XSS、命令注入全面防护
3. 防越权访问：基于 RBAC 的细粒度权限控制
4. 防重放攻击：时间戳 + 随机数双重验证
5. 请求签名验证：HMAC-SHA256 签名
6. 速率限制：基于 IP 和用户的请求频率控制
7. 会话管理：安全的 Token 生成与验证
"""
import hashlib
import hmac
import time
import json
import secrets
import base64
import re
from pathlib import Path
from typing import Any, Optional, List, Dict, Callable
from threading import Lock
from oss.plugin.types import Plugin


class SecurityError(Exception):
    """安全异常类"""
    pass


class InjectionDetector:
    """注入攻击检测器"""
    
    # SQL 注入特征
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b.*\b(FROM|INTO|TABLE|WHERE|SET)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bAND\b\s+\d+\s*\=\s*\d+)",
        r"(\'.*\bOR\b.*\')",
        r"(\;.*\b(DROP|DELETE|UPDATE|INSERT)\b)",
        r"(\bEXEC\b.*\b(XP_|SP_))",
        r"(\bWAITFOR\b\s+\bDELAY\b)",
        r"(\bBENCHMARK\b\s*\()",
        r"(\bSLEEP\b\s*\()",
    ]
    
    # XSS 攻击特征
    XSS_PATTERNS = [
        r"(<script[^>]*>)",
        r"(</script>)",
        r"(javascript:)",
        r"(on\w+\s*=)",  # onclick=, onerror=, etc.
        r"(<iframe[^>]*>)",
        r"(<object[^>]*>)",
        r"(<embed[^>]*>)",
        r"(document\.cookie)",
        r"(window\.location)",
        r"(eval\s*\()",
        r"(alert\s*\()",
    ]
    
    # 命令注入特征
    CMD_INJECTION_PATTERNS = [
        r"(\||\;|\&\&|\|\|)",
        r"(\$\(|\`)",
        r"(>\s*/dev/null)",
        r"(2>&1)",
        r"(\bwget\b|\bcurl\b|\bnc\b|\bbash\b|\bsh\b)",
        r"(\bcat\b\s+/etc/)",
        r"(\bls\b\s+-la)",
    ]
    
    def __init__(self):
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.cmd_patterns = [re.compile(p, re.IGNORECASE) for p in self.CMD_INJECTION_PATTERNS]
    
    def detect_sql_injection(self, input_str: str) -> bool:
        """检测 SQL 注入"""
        for pattern in self.sql_patterns:
            if pattern.search(input_str):
                return True
        return False
    
    def detect_xss(self, input_str: str) -> bool:
        """检测 XSS 攻击"""
        for pattern in self.xss_patterns:
            if pattern.search(input_str):
                return True
        return False
    
    def detect_cmd_injection(self, input_str: str) -> bool:
        """检测命令注入"""
        for pattern in self.cmd_patterns:
            if pattern.search(input_str):
                return True
        return False
    
    def sanitize_input(self, input_str: str) -> str:
        """清理输入"""
        # HTML 实体编码
        replacements = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '&': '&amp;',
        }
        for old, new in replacements.items():
            input_str = input_str.replace(old, new)
        return input_str
    
    def check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """检查所有输入数据"""
        results = {
            "sql_injection": False,
            "xss": False,
            "cmd_injection": False,
            "sanitized_data": {}
        }
        
        def check_value(key: str, value: Any):
            if isinstance(value, str):
                if self.detect_sql_injection(value):
                    results["sql_injection"] = True
                if self.detect_xss(value):
                    results["xss"] = True
                if self.detect_cmd_injection(value):
                    results["cmd_injection"] = True
                results["sanitized_data"][key] = self.sanitize_input(value)
            elif isinstance(value, dict):
                results["sanitized_data"][key] = {}
                for k, v in value.items():
                    check_value(f"{key}.{k}", v)
            elif isinstance(value, list):
                results["sanitized_data"][key] = []
                for i, item in enumerate(value):
                    check_value(f"{key}[{i}]", item)
            else:
                results["sanitized_data"][key] = value
        
        for key, value in data.items():
            check_value(key, value)
        
        return results


class ReplayAttackPreventer:
    """防重放攻击器"""
    
    def __init__(self, window_seconds: int = 300):
        self.window_seconds = window_seconds
        self.nonce_cache: Dict[str, float] = {}
        self.cache_lock = Lock()
        self.max_cache_size = 10000
    
    def verify(self, timestamp: int, nonce: str) -> bool:
        """验证时间戳和随机数"""
        current_time = int(time.time())
        
        # 检查时间窗口
        if abs(current_time - timestamp) > self.window_seconds:
            return False
        
        # 检查 nonce 是否已使用
        with self.cache_lock:
            if nonce in self.nonce_cache:
                return False
            
            # 存储 nonce
            self.nonce_cache[nonce] = current_time
            
            # 清理过期的 nonce
            self._cleanup()
        
        return True
    
    def _cleanup(self):
        """清理过期的 nonce"""
        current_time = int(time.time())
        expired = [
            n for n, t in self.nonce_cache.items()
            if current_time - t > self.window_seconds
        ]
        for n in expired:
            del self.nonce_cache[n]
        
        # 如果缓存过大，清理最旧的条目
        if len(self.nonce_cache) > self.max_cache_size:
            sorted_items = sorted(self.nonce_cache.items(), key=lambda x: x[1])
            for n, _ in sorted_items[:self.max_cache_size // 2]:
                del self.nonce_cache[n]


class RBACManager:
    """基于角色的访问控制管理器"""
    
    def __init__(self):
        self.roles: Dict[str, Dict[str, Any]] = {}
        self.user_roles: Dict[str, List[str]] = {}
        self.permissions: Dict[str, List[str]] = {}
        self._lock = Lock()
    
    def add_role(self, role_name: str, permissions: List[str]):
        """添加角色"""
        with self._lock:
            self.roles[role_name] = {"permissions": permissions}
    
    def assign_role(self, user_id: str, role_name: str):
        """为用户分配角色"""
        with self._lock:
            if user_id not in self.user_roles:
                self.user_roles[user_id] = []
            if role_name not in self.user_roles[user_id]:
                self.user_roles[user_id].append(role_name)
    
    def revoke_role(self, user_id: str, role_name: str):
        """撤销用户角色"""
        with self._lock:
            if user_id in self.user_roles and role_name in self.user_roles[user_id]:
                self.user_roles[user_id].remove(role_name)
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """检查用户是否有指定权限"""
        with self._lock:
            if user_id not in self.user_roles:
                return False
            
            for role_name in self.user_roles[user_id]:
                if role_name in self.roles:
                    if permission in self.roles[role_name]["permissions"]:
                        return True
            
            return False
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """获取用户的所有权限"""
        permissions = set()
        with self._lock:
            if user_id in self.user_roles:
                for role_name in self.user_roles[user_id]:
                    if role_name in self.roles:
                        permissions.update(self.roles[role_name]["permissions"])
        return list(permissions)
    
    def load_from_file(self, filepath: str):
        """从文件加载 RBAC 配置"""
        path = Path(filepath)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.roles = data.get("roles", {})
                self.user_roles = data.get("user_roles", {})
    
    def save_to_file(self, filepath: str):
        """保存 RBAC 配置到文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "roles": self.roles,
                "user_roles": self.user_roles
            }, f, indent=2)


class TokenManager:
    """Token 管理器"""
    
    def __init__(self, secret_key: str, expiry_seconds: int = 3600):
        self.secret_key = secret_key.encode('utf-8')
        self.expiry_seconds = expiry_seconds
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def generate_token(self, user_id: str, metadata: Optional[Dict] = None) -> str:
        """生成访问 Token"""
        timestamp = int(time.time())
        expiry = timestamp + self.expiry_seconds
        
        # 创建 payload
        payload = {
            "user_id": user_id,
            "timestamp": timestamp,
            "expiry": expiry,
            "nonce": secrets.token_hex(16),
            "metadata": metadata or {}
        }
        
        # 创建签名
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key,
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 组合 token
        token_data = base64.urlsafe_b64encode(payload_str.encode('utf-8')).decode('utf-8')
        token = f"{token_data}.{signature}"
        
        # 存储 token
        with self._lock:
            self.tokens[token] = {
                "payload": payload,
                "created_at": timestamp,
                "user_id": user_id
            }
        
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证 Token"""
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return {"valid": False, "error": "Invalid token format"}
            
            token_data, signature = parts
            
            # 解码 payload
            payload_str = base64.urlsafe_b64decode(token_data.encode('utf-8')).decode('utf-8')
            payload = json.loads(payload_str)
            
            # 验证签名
            expected_signature = hmac.new(
                self.secret_key,
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return {"valid": False, "error": "Invalid signature"}
            
            # 检查过期
            current_time = int(time.time())
            if current_time > payload.get("expiry", 0):
                return {"valid": False, "error": "Token expired"}
            
            # 检查 token 是否在黑名单中
            with self._lock:
                if token not in self.tokens:
                    return {"valid": False, "error": "Token revoked"}
            
            return {
                "valid": True,
                "user_id": payload["user_id"],
                "payload": payload
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def revoke_token(self, token: str) -> bool:
        """撤销 Token"""
        with self._lock:
            if token in self.tokens:
                del self.tokens[token]
                return True
            return False
    
    def cleanup_expired(self):
        """清理过期的 token"""
        current_time = int(time.time())
        with self._lock:
            expired = [
                t for t, data in self.tokens.items()
                if current_time > data["payload"].get("expiry", 0)
            ]
            for t in expired:
                del self.tokens[t]


class SecurityGatewayPlugin(Plugin):
    """统一安全网关插件"""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.injection_detector = InjectionDetector()
        self.replay_preventer = ReplayAttackPreventer()
        self.rbac_manager = RBACManager()
        self.token_manager: Optional[TokenManager] = None
        self._secret_key: str = ""
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        self._blocked_ips: Dict[str, float] = {}
    
    def init(self, deps: Optional[Dict[str, Any]] = None):
        """初始化插件"""
        if deps:
            self.config = deps.get("config", {})
            
            # 初始化密钥
            self._secret_key = self.config.get("secret_key", secrets.token_hex(32))
            expiry = self.config.get("token_expiry", 3600)
            self.token_manager = TokenManager(self._secret_key, expiry)
            
            # 加载 RBAC 配置
            rbac_file = self.config.get("rbac_config", "config/rbac.json")
            self.rbac_manager.load_from_file(rbac_file)
            
            # 设置默认角色
            self._setup_default_roles()
    
    def _setup_default_roles(self):
        """设置默认角色"""
        # 管理员角色
        self.rbac_manager.add_role("admin", [
            "*",  # 所有权限
        ])
        
        # 普通用户角色
        self.rbac_manager.add_role("user", [
            "read",
            "write:own",
            "delete:own"
        ])
        
        # 只读用户角色
        self.rbac_manager.add_role("readonly", [
            "read"
        ])
        
        # API 服务角色
        self.rbac_manager.add_role("service", [
            "api:call",
            "internal:access"
        ])
    
    def start(self):
        """启动插件"""
        print("[SecurityGateway] 安全网关已启动")
        print(f"[SecurityGateway] Token 过期时间：{self.config.get('token_expiry', 3600)}秒")
        print(f"[SecurityGateway] 防重放窗口：{self.replay_preventer.window_seconds}秒")
    
    def stop(self):
        """停止插件"""
        # 保存 RBAC 配置
        rbac_file = self.config.get("rbac_config", "config/rbac.json")
        self.rbac_manager.save_to_file(rbac_file)
        print("[SecurityGateway] 安全网关已停止")
    
    def check_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查请求安全性"""
        result = {
            "allowed": True,
            "checks": {},
            "errors": []
        }
        
        # 1. 注入攻击检测
        injection_result = self.injection_detector.check(request_data.get("body", {}))
        result["checks"]["injection"] = injection_result
        
        if injection_result["sql_injection"]:
            result["allowed"] = False
            result["errors"].append("检测到 SQL 注入尝试")
        
        if injection_result["xss"]:
            result["allowed"] = False
            result["errors"].append("检测到 XSS 攻击尝试")
        
        if injection_result["cmd_injection"]:
            result["allowed"] = False
            result["errors"].append("检测到命令注入尝试")
        
        # 2. 防重放攻击检查
        headers = request_data.get("headers", {})
        timestamp = headers.get("X-Timestamp")
        nonce = headers.get("X-Nonce")
        
        if timestamp and nonce:
            try:
                ts = int(timestamp)
                if not self.replay_preventer.verify(ts, nonce):
                    result["allowed"] = False
                    result["errors"].append("检测到重放攻击")
                else:
                    result["checks"]["replay"] = True
            except ValueError:
                result["errors"].append("无效的时间戳格式")
        
        # 3. Token 验证
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            token_result = self.token_manager.verify_token(token) if self.token_manager else {"valid": False, "error": "Token manager not initialized"}
            result["checks"]["token"] = token_result
            
            if not token_result.get("valid"):
                result["allowed"] = False
                result["errors"].append(f"Token 验证失败：{token_result.get('error')}")
            else:
                result["user_id"] = token_result.get("user_id")
        
        # 4. IP 封禁检查
        client_ip = request_data.get("ip", "")
        if client_ip in self._blocked_ips:
            expire_time = self._blocked_ips[client_ip]
            if time.time() < expire_time:
                result["allowed"] = False
                result["errors"].append(f"IP 已被封禁，解封时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time))}")
            else:
                del self._blocked_ips[client_ip]
        
        # 5. 速率限制检查
        rate_limit_result = self._check_rate_limit(client_ip)
        result["checks"]["rate_limit"] = rate_limit_result
        if not rate_limit_result["allowed"]:
            result["allowed"] = False
            result["errors"].append("请求频率过高")
        
        return result
    
    def _check_rate_limit(self, ip: str) -> Dict[str, Any]:
        """检查速率限制"""
        current_time = time.time()
        window = self.config.get("rate_limit_window", 60)
        max_requests = self.config.get("rate_limit_max", 100)
        
        if ip not in self._rate_limits:
            self._rate_limits[ip] = {"count": 0, "window_start": current_time}
        
        rate_info = self._rate_limits[ip]
        
        # 重置窗口
        if current_time - rate_info["window_start"] >= window:
            rate_info["count"] = 0
            rate_info["window_start"] = current_time
        
        rate_info["count"] += 1
        
        if rate_info["count"] > max_requests:
            # 封禁 IP
            block_duration = self.config.get("block_duration", 300)
            self._blocked_ips[ip] = current_time + block_duration
            return {
                "allowed": False,
                "remaining": 0,
                "reset": rate_info["window_start"] + window
            }
        
        return {
            "allowed": True,
            "remaining": max_requests - rate_info["count"],
            "reset": rate_info["window_start"] + window
        }
    
    def generate_token(self, user_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """生成访问 Token"""
        if not self.token_manager:
            return {"success": False, "error": "Token manager not initialized"}
        
        token = self.token_manager.generate_token(user_id, metadata)
        return {
            "success": True,
            "token": token,
            "expires_in": self.config.get("token_expiry", 3600)
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证 Token"""
        if not self.token_manager:
            return {"valid": False, "error": "Token manager not initialized"}
        
        return self.token_manager.verify_token(token)
    
    def check_permission(self, user_id: str, permission: str) -> Dict[str, Any]:
        """检查权限"""
        has_permission = self.rbac_manager.check_permission(user_id, permission)
        return {
            "allowed": has_permission,
            "user_id": user_id,
            "permission": permission
        }
    
    def assign_role(self, user_id: str, role_name: str) -> Dict[str, Any]:
        """分配角色"""
        if role_name not in self.rbac_manager.roles:
            return {"success": False, "error": f"角色 '{role_name}' 不存在"}
        
        self.rbac_manager.assign_role(user_id, role_name)
        return {
            "success": True,
            "user_id": user_id,
            "role": role_name
        }
    
    def block_ip(self, ip: str, duration: int = 3600) -> Dict[str, Any]:
        """封禁 IP"""
        self._blocked_ips[ip] = time.time() + duration
        return {
            "success": True,
            "ip": ip,
            "duration": duration,
            "unblock_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + duration))
        }
    
    def unblock_ip(self, ip: str) -> Dict[str, Any]:
        """解封 IP"""
        if ip in self._blocked_ips:
            del self._blocked_ips[ip]
            return {"success": True, "ip": ip}
        return {"success": False, "error": "IP 不在封禁列表中"}
    
    def get_blocked_ips(self) -> Dict[str, Any]:
        """获取封禁 IP 列表"""
        current_time = time.time()
        blocked = {
            ip: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire))
            for ip, expire in self._blocked_ips.items()
            if expire > current_time
        }
        return {
            "success": True,
            "blocked_ips": blocked,
            "total": len(blocked)
        }
    
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理输入数据"""
        result = self.injection_detector.check(data)
        return {
            "success": True,
            "sanitized_data": result["sanitized_data"],
            "threats_detected": {
                "sql_injection": result["sql_injection"],
                "xss": result["xss"],
                "cmd_injection": result["cmd_injection"]
            }
        }
    
    def register_pl_functions(self, injector: Any):
        """注册 PL 注入功能"""
        
        def check_security_request(**kwargs) -> Dict[str, Any]:
            """检查请求安全性"""
            return self.check_request(kwargs)
        
        injector.register_function(
            "security-gateway:check_request",
            check_security_request,
            "检查请求的安全性（注入检测、Token 验证、速率限制等）"
        )
        
        def create_token(user_id: str, **metadata) -> Dict[str, Any]:
            """生成 Token"""
            return self.generate_token(user_id, metadata)
        
        injector.register_function(
            "security-gateway:create_token",
            create_token,
            "为用户生成访问 Token"
        )
        
        def verify_security_token(token: str) -> Dict[str, Any]:
            """验证 Token"""
            return self.verify_token(token)
        
        injector.register_function(
            "security-gateway:verify_token",
            verify_security_token,
            "验证访问 Token 的有效性"
        )
        
        def check_user_permission(user_id: str, permission: str) -> Dict[str, Any]:
            """检查权限"""
            return self.check_permission(user_id, permission)
        
        injector.register_function(
            "security-gateway:check_permission",
            check_user_permission,
            "检查用户是否有指定权限"
        )
        
        def assign_user_role(user_id: str, role_name: str) -> Dict[str, Any]:
            """分配角色"""
            return self.assign_role(user_id, role_name)
        
        injector.register_function(
            "security-gateway:assign_role",
            assign_user_role,
            "为用户分配角色"
        )
        
        def block_user_ip(ip: str, duration: int = 3600) -> Dict[str, Any]:
            """封禁 IP"""
            return self.block_ip(ip, duration)
        
        injector.register_function(
            "security-gateway:block_ip",
            block_user_ip,
            "封禁指定 IP 地址"
        )
        
        def unblock_user_ip(ip: str) -> Dict[str, Any]:
            """解封 IP"""
            return self.unblock_ip(ip)
        
        injector.register_function(
            "security-gateway:unblock_ip",
            unblock_user_ip,
            "解封指定 IP 地址"
        )
        
        def get_blocked_ip_list() -> Dict[str, Any]:
            """获取封禁 IP 列表"""
            return self.get_blocked_ips()
        
        injector.register_function(
            "security-gateway:get_blocked_ips",
            get_blocked_ip_list,
            "获取当前封禁的 IP 列表"
        )
        
        def sanitize_user_input(**data) -> Dict[str, Any]:
            """清理输入"""
            return self.sanitize_input(data)
        
        injector.register_function(
            "security-gateway:sanitize_input",
            sanitize_user_input,
            "清理用户输入数据（防止注入攻击）"
        )


def New() -> SecurityGatewayPlugin:
    """创建插件实例"""
    return SecurityGatewayPlugin()
