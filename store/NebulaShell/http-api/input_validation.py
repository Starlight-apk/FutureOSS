"""
输入验证中间件
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from oss.config import get_config
from oss.logger.logger import Log
from .server import Request, Response


class InputValidator:
    """输入验证器"""
    
    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.get("INPUT_VALIDATION_ENABLED", True)
        
        # 预定义的模式
        self.patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "username": r'^[a-zA-Z0-9_]{3,20}$',
            "password": r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$',
            "api_key": r'^[a-zA-Z0-9_-]{32,}$',
            "uuid": r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            "ip_address": r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            "url": r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&]*$'
        }
        
        # 端点特定的验证规则
        self.endpoint_rules = {
            "/api/auth/login": {
                "methods": ["POST"],
                "required_fields": ["username", "password"],
                "field_rules": {
                    "username": {"type": "str", "min_length": 3, "max_length": 20, "pattern": "username"},
                    "password": {"type": "str", "min_length": 8, "max_length": 100}
                }
            },
            "/api/auth/register": {
                "methods": ["POST"],
                "required_fields": ["username", "email", "password"],
                "field_rules": {
                    "username": {"type": "str", "min_length": 3, "max_length": 20, "pattern": "username"},
                    "email": {"type": "str", "pattern": "email"},
                    "password": {"type": "str", "min_length": 8, "max_length": 100, "pattern": "password"}
                }
            },
            "/api/users": {
                "methods": ["GET", "POST"],
                "field_rules": {
                    "limit": {"type": "int", "min_value": 1, "max_value": 100},
                    "offset": {"type": "int", "min_value": 0},
                    "search": {"type": "str", "max_length": 100}
                }
            },
            "/api/pkg-manager/search": {
                "methods": ["GET"],
                "field_rules": {
                    "query": {"type": "str", "min_length": 1, "max_length": 100},
                    "limit": {"type": "int", "min_value": 1, "max_value": 50},
                    "page": {"type": "int", "min_value": 1}
                }
            }
        }
    
    def validate_field(self, field_name: str, value: Any, rules: Dict) -> Optional[str]:
        """验证单个字段"""
        # 类型验证
        if "type" in rules:
            expected_type = rules["type"]
            if expected_type == "str" and not isinstance(value, str):
                return f"{field_name} 必须是字符串"
            elif expected_type == "int" and not isinstance(value, int):
                return f"{field_name} 必须是整数"
            elif expected_type == "float" and not isinstance(value, (int, float)):
                return f"{field_name} 必须是数字"
            elif expected_type == "bool" and not isinstance(value, bool):
                return f"{field_name} 必须是布尔值"
        
        # 长度验证
        if isinstance(value, str):
            if "min_length" in rules and len(value) < rules["min_length"]:
                return f"{field_name} 长度不能少于 {rules['min_length']} 个字符"
            if "max_length" in rules and len(value) > rules["max_length"]:
                return f"{field_name} 长度不能超过 {rules['max_length']} 个字符"
        
        # 数值范围验证
        if isinstance(value, (int, float)):
            if "min_value" in rules and value < rules["min_value"]:
                return f"{field_name} 不能小于 {rules['min_value']}"
            if "max_value" in rules and value > rules["max_value"]:
                return f"{field_name} 不能大于 {rules['max_value']}"
        
        # 模式验证
        if "pattern" in rules and isinstance(value, str):
            pattern = self.patterns.get(rules["pattern"])
            if pattern and not re.match(pattern, value):
                return f"{field_name} 格式不正确"
        
        # 枚举验证
        if "choices" in rules and value not in rules["choices"]:
            return f"{field_name} 必须是以下值之一: {', '.join(rules['choices'])}"
        
        return None
    
    def validate_request(self, request: Request) -> Optional[str]:
        """验证请求"""
        if not self.enabled:
            return None
        
        # 检查是否有对应的验证规则
        rules = None
        for endpoint, rule in self.endpoint_rules.items():
            if request.path.startswith(endpoint):
                rules = rule
                break
        
        if not rules:
            return None
        
        # 检查请求方法
        if "methods" in rules and request.method not in rules["methods"]:
            return f"不支持的请求方法: {request.method}"
        
        # 解析请求体
        body_data = {}
        if request.method in ["POST", "PUT", "PATCH"] and request.body:
            try:
                body_data = json.loads(request.body)
            except json.JSONDecodeError:
                return "无效的JSON格式"
        
        # 解析查询参数
        query_params = {}
        if request.query:
            try:
                query_params = json.loads(request.query)
            except:
                # 如果不是JSON，按简单键值对处理
                query_params = {}
        
        # 检查必需字段
        if "required_fields" in rules:
            for field in rules["required_fields"]:
                if field not in body_data and field not in query_params:
                    return f"缺少必需字段: {field}"
        
        # 验证字段规则
        if "field_rules" in rules:
            all_data = {**body_data, **query_params}
            
            for field_name, field_rules in rules["field_rules"].items():
                if field_name in all_data:
                    error = self.validate_field(field_name, all_data[field_name], field_rules)
                    if error:
                        return error
        
        return None


class InputValidationMiddleware:
    """输入验证中间件"""
    
    def __init__(self):
        self.config = get_config()
        self.enabled = self.config.get("INPUT_VALIDATION_ENABLED", True)
        self.validator = InputValidator()
        
        # 豁免路径（不进行验证）
        self.exempt_paths = {
            "/health", "/favicon.ico", "/api/status", 
            "/api/health", "/metrics"
        }
    
    def create_validation_error_response(self, error_message: str) -> Response:
        """创建验证错误响应"""
        return Response(
            status=400,
            body=json.dumps({
                "error": "Validation Error",
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            }),
            headers={"Content-Type": "application/json"}
        )
    
    def process(self, ctx: dict, next_fn) -> Optional[Response]:
        """处理输入验证逻辑"""
        if not self.enabled:
            return next_fn()
        
        request = ctx.get("request")
        if not request:
            return next_fn()
        
        # 检查是否为豁免路径
        if request.path in self.exempt_paths:
            return next_fn()
        
        # 验证请求
        validation_error = self.validator.validate_request(request)
        if validation_error:
            Log.warn("validation", f"输入验证失败: {validation_error} ({request.method} {request.path})")
            return self.create_validation_error_response(validation_error)
        
        return next_fn()