"""
FutureOSS v1.1.0 - 动态防火墙插件
功能：IP 过滤、端口管理、规则引擎、攻击检测
"""
import os
import json
import logging
import ipaddress
from datetime import datetime
from typing import Dict, List, Set, Optional
from oss.plugin.base import BasePlugin
from oss.core.context import Context

logger = logging.getLogger("futureoss.firewall")

class FirewallPlugin(BasePlugin):
    name = "firewall"
    version = "1.1.0"
    description = "动态防火墙：智能 IP 过滤与端口管理"
    
    def __init__(self):
        super().__init__()
        self.rules_file = "./config/firewall_rules.json"
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self.blocked_ports: Set[int] = set()
        self.allowed_ports: Set[int] = {80, 443, 22}  # 默认开放端口
        self.rate_limits: Dict[str, Dict] = {}
        self.attack_log: List[Dict] = []
        
        # 加载现有规则
        self.load_rules()

    def on_load(self, ctx: Context):
        logger.info("动态防火墙已启动")
        
        # 注册命令
        ctx.register_command("firewall.ip.allow", self.allow_ip)
        ctx.register_command("firewall.ip.block", self.block_ip)
        ctx.register_command("firewall.ip.list", self.list_ips)
        ctx.register_command("firewall.port.open", self.open_port)
        ctx.register_command("firewall.port.close", self.close_port)
        ctx.register_command("firewall.port.list", self.list_ports)
        ctx.register_command("firewall.rule.add", self.add_rule)
        ctx.register_command("firewall.rule.list", self.list_rules)
        ctx.register_command("firewall.attack.log", self.get_attack_log)

    def load_rules(self):
        """加载防火墙规则"""
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, "r") as f:
                    rules = json.load(f)
                    self.whitelist = set(rules.get("whitelist", []))
                    self.blacklist = set(rules.get("blacklist", []))
                    self.blocked_ports = set(rules.get("blocked_ports", []))
                    self.allowed_ports = set(rules.get("allowed_ports", [80, 443, 22]))
                logger.info(f"已加载 {len(self.whitelist)} 个白名单 IP, {len(self.blacklist)} 个黑名单 IP")
            except Exception as e:
                logger.error(f"加载防火墙规则失败：{e}")

    def save_rules(self):
        """保存防火墙规则"""
        rules = {
            "whitelist": list(self.whitelist),
            "blacklist": list(self.blacklist),
            "blocked_ports": list(self.blocked_ports),
            "allowed_ports": list(self.allowed_ports),
            "updated_at": datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        with open(self.rules_file, "w") as f:
            json.dump(rules, f, indent=2)

    def allow_ip(self, ctx: Context, ip: str):
        """添加 IP 到白名单"""
        try:
            ipaddress.ip_address(ip)
            self.whitelist.add(ip)
            self.blacklist.discard(ip)  # 从黑名单移除
            self.save_rules()
            logger.info(f"IP {ip} 已加入白名单")
            return {"status": "success", "message": f"IP {ip} 已加入白名单"}
        except ValueError:
            return {"status": "error", "message": "无效的 IP 地址"}

    def block_ip(self, ctx: Context, ip: str, reason: str = ""):
        """添加 IP 到黑名单"""
        try:
            ipaddress.ip_address(ip)
            self.blacklist.add(ip)
            self.whitelist.discard(ip)  # 从白名单移除
            self.save_rules()
            
            # 记录攻击日志
            self.attack_log.append({
                "timestamp": datetime.now().isoformat(),
                "ip": ip,
                "action": "blocked",
                "reason": reason
            })
            
            logger.warning(f"IP {ip} 已加入黑名单，原因：{reason}")
            return {"status": "success", "message": f"IP {ip} 已加入黑名单"}
        except ValueError:
            return {"status": "error", "message": "无效的 IP 地址"}

    def list_ips(self, ctx: Context):
        """列出所有 IP 规则"""
        return {
            "status": "success",
            "whitelist": list(self.whitelist),
            "blacklist": list(self.blacklist),
            "total": len(self.whitelist) + len(self.blacklist)
        }

    def open_port(self, ctx: Context, port: int):
        """开放端口"""
        if not (0 < port < 65536):
            return {"status": "error", "message": "无效端口号"}
        
        self.allowed_ports.add(port)
        self.blocked_ports.discard(port)
        self.save_rules()
        logger.info(f"端口 {port} 已开放")
        return {"status": "success", "message": f"端口 {port} 已开放"}

    def close_port(self, ctx: Context, port: int):
        """关闭端口"""
        if not (0 < port < 65536):
            return {"status": "error", "message": "无效端口号"}
        
        self.blocked_ports.add(port)
        self.allowed_ports.discard(port)
        self.save_rules()
        logger.info(f"端口 {port} 已关闭")
        return {"status": "success", "message": f"端口 {port} 已关闭"}

    def list_ports(self, ctx: Context):
        """列出端口规则"""
        return {
            "status": "success",
            "allowed_ports": sorted(list(self.allowed_ports)),
            "blocked_ports": sorted(list(self.blocked_ports))
        }

    def add_rule(self, ctx: Context, rule_type: str, **kwargs):
        """添加高级规则"""
        rule = {
            "type": rule_type,
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        
        if rule_type == "rate_limit":
            ip = kwargs.get("ip")
            limit = kwargs.get("limit", 100)  # 每秒请求数
            self.rate_limits[ip] = {"limit": limit, "window": 1}
            logger.info(f"为 IP {ip} 设置限流：{limit} req/s")
        
        return {"status": "success", "rule": rule}

    def list_rules(self, ctx: Context):
        """列出所有规则"""
        return {
            "status": "success",
            "whitelist_count": len(self.whitelist),
            "blacklist_count": len(self.blacklist),
            "allowed_ports_count": len(self.allowed_ports),
            "blocked_ports_count": len(self.blocked_ports),
            "rate_limits": self.rate_limits
        }

    def get_attack_log(self, ctx: Context, limit: int = 50):
        """获取攻击日志"""
        return {
            "status": "success",
            "logs": self.attack_log[-limit:],
            "total": len(self.attack_log)
        }

    def check_ip(self, ip: str) -> bool:
        """检查 IP 是否允许访问"""
        if ip in self.whitelist:
            return True
        if ip in self.blacklist:
            return False
        return True  # 默认允许

    def check_port(self, port: int) -> bool:
        """检查端口是否开放"""
        return port in self.allowed_ports and port not in self.blocked_ports

    def on_unload(self, ctx: Context):
        self.save_rules()
        logger.info("动态防火墙已停止")
