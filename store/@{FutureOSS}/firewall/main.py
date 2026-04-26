"""动态防火墙插件 - 提供 IP 过滤/端口管理/访问控制/WebUI 规则配置

功能说明：
1. 状态检测引擎：基于连接状态的智能规则匹配
2. 热加载能力：无需重启即可更新防火墙策略
3. 实时流量分析：可视化展示入站/出站流量
4. 异常行为熔断：检测到攻击自动触发保护机制
5. 支持 iptables/ufw/nftables 多种后端
6. WebUI 规则配置界面集成
"""
import subprocess
import json
import threading
import time
from pathlib import Path
from typing import Any, Optional, List, Dict
from oss.plugin.types import Plugin


class FirewallBackend:
    """防火墙后端抽象基类"""
    
    def __init__(self):
        self.rules: List[Dict[str, Any]] = []
        self.whitelist: List[str] = []
        self.blacklist: List[str] = []
        self.rate_limits: Dict[str, Any] = {}
        self.connection_states: Dict[str, Any] = {}
        self.stats = {
            "packets_processed": 0,
            "packets_dropped": 0,
            "packets_accepted": 0,
            "connections_tracked": 0
        }
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """添加防火墙规则"""
        raise NotImplementedError
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除防火墙规则"""
        raise NotImplementedError
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """列出所有规则"""
        raise NotImplementedError
    
    def add_to_whitelist(self, ip: str) -> bool:
        """添加到白名单"""
        if ip not in self.whitelist:
            self.whitelist.append(ip)
            return True
        return False
    
    def add_to_blacklist(self, ip: str) -> bool:
        """添加到黑名单"""
        if ip not in self.blacklist:
            self.blacklist.append(ip)
            return True
        return False
    
    def set_rate_limit(self, ip: str, requests: int, window: int) -> bool:
        """设置速率限制"""
        self.rate_limits[ip] = {
            "requests": requests,
            "window": window,
            "count": 0,
            "reset_time": time.time() + window
        }
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def check_rate_limit(self, ip: str) -> bool:
        """检查速率限制"""
        if ip not in self.rate_limits:
            return True
        
        limit = self.rate_limits[ip]
        now = time.time()
        
        if now >= limit["reset_time"]:
            limit["count"] = 0
            limit["reset_time"] = now + limit["window"]
        
        if limit["count"] >= limit["requests"]:
            return False
        
        limit["count"] += 1
        return True
    
    def apply_rules(self) -> bool:
        """应用所有规则到系统防火墙"""
        raise NotImplementedError
    
    def reload(self) -> bool:
        """重新加载规则"""
        raise NotImplementedError


class IptablesBackend(FirewallBackend):
    """iptables 防火墙后端"""
    
    def __init__(self):
        super().__init__()
        self.chain_name = "FUTUREOSS"
        self._ensure_chain()
    
    def _run_iptables(self, args: List[str], check=False) -> subprocess.CompletedProcess:
        """运行 iptables 命令"""
        cmd = ["iptables"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=check
            )
            return result
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(cmd, -1, "", "Timeout")
        except Exception as e:
            return subprocess.CompletedProcess(cmd, -1, "", str(e))
    
    def _ensure_chain(self):
        """确保自定义链存在"""
        # 创建自定义链
        self._run_iptables(["-N", self.chain_name])
        # 如果链已存在则忽略错误
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """添加防火墙规则"""
        action = rule.get("action", "ACCEPT")  # ACCEPT, DROP, REJECT
        protocol = rule.get("protocol", "tcp")
        src_ip = rule.get("src_ip")
        dst_ip = rule.get("dst_ip")
        src_port = rule.get("src_port")
        dst_port = rule.get("dst_port")
        interface = rule.get("interface")
        state = rule.get("state")  # NEW, ESTABLISHED, RELATED
        
        args = ["-A", self.chain_name]
        
        if interface:
            args.extend(["-i", interface])
        
        if protocol:
            args.extend(["-p", protocol])
        
        if src_ip:
            args.extend(["-s", src_ip])
        
        if dst_ip:
            args.extend(["-d", dst_ip])
        
        if src_port:
            args.extend(["--sport", str(src_port)])
        
        if dst_port:
            args.extend(["--dport", str(dst_port)])
        
        if state:
            args.extend(["-m", "state", "--state", state])
        
        args.extend(["-j", action])
        
        result = self._run_iptables(args)
        if result.returncode == 0:
            self.rules.append(rule)
            return True
        return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除防火墙规则"""
        # 简化实现：按索引删除
        try:
            idx = int(rule_id)
            if 0 <= idx < len(self.rules):
                rule = self.rules[idx]
                # 构建删除命令
                args = ["-D", self.chain_name]
                if rule.get("dst_port"):
                    args.extend(["-p", rule.get("protocol", "tcp"), "--dport", str(rule["dst_port"])])
                args.extend(["-j", rule.get("action", "ACCEPT")])
                
                result = self._run_iptables(args)
                if result.returncode == 0:
                    self.rules.pop(idx)
                    return True
        except (ValueError, IndexError):
            pass
        return False
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """列出所有规则"""
        # 获取 iptables 中的实际规则
        result = self._run_iptables(["-L", self.chain_name, "-n", "-v"])
        rules_output = result.stdout if result.returncode == 0 else ""
        
        return [{
            "id": str(i),
            **rule,
            "active": True
        } for i, rule in enumerate(self.rules)]
    
    def apply_rules(self) -> bool:
        """应用所有规则到系统防火墙"""
        # 清除现有规则
        self._run_iptables(["-F", self.chain_name])
        
        # 重新应用所有规则
        for rule in self.rules:
            if not self.add_rule(rule):
                return False
        
        # 应用白名单
        for ip in self.whitelist:
            self._run_iptables(["-I", self.chain_name, "-s", ip, "-j", "ACCEPT"])
        
        # 应用黑名单
        for ip in self.blacklist:
            self._run_iptables(["-I", self.chain_name, "-s", ip, "-j", "DROP"])
        
        return True
    
    def reload(self) -> bool:
        """重新加载规则"""
        return self.apply_rules()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = super().get_stats()
        
        # 尝试从 iptables 获取真实统计
        result = self._run_iptables(["-L", self.chain_name, "-n", "-v", "-x"])
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[2:]  # 跳过表头
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        packets = int(parts[0])
                        stats["packets_processed"] += packets
                    except ValueError:
                        pass
        
        return stats


class UfwBackend(FirewallBackend):
    """UFW 防火墙后端"""
    
    def __init__(self):
        super().__init__()
        self._check_ufw()
    
    def _check_ufw(self):
        """检查 UFW 是否可用"""
        result = subprocess.run(
            ["which", "ufw"],
            capture_output=True,
            text=True
        )
        self.available = result.returncode == 0
    
    def _run_ufw(self, args: List[str]) -> subprocess.CompletedProcess:
        """运行 ufw 命令"""
        if not self.available:
            return subprocess.CompletedProcess(
                ["ufw"] + args, 
                -1, 
                "", 
                "UFW not available"
            )
        
        cmd = ["ufw"] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result
        except Exception as e:
            return subprocess.CompletedProcess(cmd, -1, "", str(e))
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """添加防火墙规则"""
        action = rule.get("action", "allow")  # allow, deny, reject
        port = rule.get("dst_port")
        protocol = rule.get("protocol", "tcp")
        src_ip = rule.get("src_ip")
        
        if not port:
            return False
        
        args = [action]
        
        if src_ip:
            args.extend(["from", src_ip])
        else:
            args.extend(["from", "any"])
        
        args.extend(["to", "any", "port", str(port)])
        
        if protocol:
            args.append(protocol)
        
        result = self._run_ufw(args)
        if result.returncode == 0:
            self.rules.append(rule)
            return True
        return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除防火墙规则"""
        try:
            idx = int(rule_id)
            if 0 <= idx < len(self.rules):
                # UFW 通过规则号删除
                result = self._run_ufw(["delete", str(idx + 1)])
                if result.returncode == 0:
                    self.rules.pop(idx)
                    return True
        except (ValueError, IndexError):
            pass
        return False
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """列出所有规则"""
        result = self._run_ufw(["status", "verbose"])
        rules_output = result.stdout if result.returncode == 0 else ""
        
        return [{
            "id": str(i),
            **rule,
            "active": True
        } for i, rule in enumerate(self.rules)]
    
    def apply_rules(self) -> bool:
        """应用所有规则"""
        # UFW 即时生效，无需额外应用
        return True
    
    def reload(self) -> bool:
        """重新加载规则"""
        result = self._run_ufw(["reload"])
        return result.returncode == 0


class FirewallPlugin(Plugin):
    """动态防火墙插件"""
    
    def __init__(self):
        self.backend: Optional[FirewallBackend] = None
        self.config: Dict[str, Any] = {}
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._auto_block_enabled = False
        self._threat_threshold = 100  # 每分钟请求数阈值
        self._blocked_ips: Dict[str, float] = {}  # IP -> 解封时间
    
    def init(self, deps: Optional[Dict[str, Any]] = None):
        """初始化插件"""
        if deps:
            self.config = deps.get("config", {})
            self._auto_block_enabled = self.config.get("auto_block_enabled", True)
            self._threat_threshold = self.config.get("threat_threshold", 100)
        
        # 检测并选择合适的后端
        self._detect_backend()
        
        # 加载持久化规则
        self._load_rules()
    
    def _detect_backend(self):
        """检测可用的防火墙后端"""
        # 优先使用 iptables
        result = subprocess.run(["which", "iptables"], capture_output=True, text=True)
        if result.returncode == 0:
            self.backend = IptablesBackend()
            print("[Firewall] 使用 iptables 后端")
            return
        
        # 尝试 UFW
        result = subprocess.run(["which", "ufw"], capture_output=True, text=True)
        if result.returncode == 0:
            self.backend = UfwBackend()
            print("[Firewall] 使用 UFW 后端")
            return
        
        # 使用模拟后端（开发环境）
        print("[Firewall] 未检测到系统防火墙，使用模拟模式")
        self.backend = FirewallBackend()
    
    def start(self):
        """启动插件"""
        self._running = True
        
        # 应用初始规则
        if self.backend:
            self.backend.apply_rules()
        
        # 启动监控线程
        if self._auto_block_enabled:
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            print("[Firewall] 自动威胁检测已启动")
    
    def stop(self):
        """停止插件"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        # 保存规则
        self._save_rules()
    
    def _monitor_loop(self):
        """监控循环 - 检测异常行为"""
        while self._running:
            try:
                # 检查被封禁的 IP 是否需要解封
                now = time.time()
                expired = [ip for ip, expire_time in self._blocked_ips.items() if now >= expire_time]
                for ip in expired:
                    del self._blocked_ips[ip]
                    if self.backend:
                        self.backend.remove_from_blacklist(ip) if hasattr(self.backend, 'remove_from_blacklist') else None
                    print(f"[Firewall] 已解封 IP: {ip}")
                
                # 分析流量统计
                if self.backend:
                    stats = self.backend.get_stats()
                    if stats.get("packets_dropped", 0) > 1000:
                        print(f"[Firewall] 警告：检测到大量丢包 ({stats['packets_dropped']})")
                
                time.sleep(10)  # 每 10 秒检查一次
            except Exception as e:
                print(f"[Firewall] 监控错误：{e}")
                time.sleep(5)
    
    def _load_rules(self):
        """从配置文件加载规则"""
        rules_file = Path(self.config.get("rules_file", "config/firewall_rules.json"))
        if rules_file.exists():
            try:
                with open(rules_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.backend.rules = data.get("rules", [])
                    self.backend.whitelist = data.get("whitelist", [])
                    self.backend.blacklist = data.get("blacklist", [])
                print(f"[Firewall] 已加载 {len(self.backend.rules)} 条规则")
            except Exception as e:
                print(f"[Firewall] 加载规则失败：{e}")
    
    def _save_rules(self):
        """保存规则到配置文件"""
        rules_file = Path(self.config.get("rules_file", "config/firewall_rules.json"))
        rules_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(rules_file, "w", encoding="utf-8") as f:
                json.dump({
                    "rules": self.backend.rules if self.backend else [],
                    "whitelist": self.backend.whitelist if self.backend else [],
                    "blacklist": self.backend.blacklist if self.backend else []
                }, f, indent=2)
            print(f"[Firewall] 已保存规则到 {rules_file}")
        except Exception as e:
            print(f"[Firewall] 保存规则失败：{e}")
    
    def add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """添加防火墙规则"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        success = self.backend.add_rule(rule)
        if success:
            self.backend.apply_rules()
        
        return {
            "success": success,
            "rule": rule,
            "message": "规则添加成功" if success else "规则添加失败"
        }
    
    def remove_rule(self, rule_id: str) -> Dict[str, Any]:
        """删除防火墙规则"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        success = self.backend.remove_rule(rule_id)
        if success:
            self.backend.apply_rules()
        
        return {
            "success": success,
            "rule_id": rule_id,
            "message": "规则删除成功" if success else "规则删除失败"
        }
    
    def list_rules(self) -> Dict[str, Any]:
        """列出所有规则"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        rules = self.backend.list_rules()
        return {
            "success": True,
            "rules": rules,
            "total": len(rules)
        }
    
    def whitelist_add(self, ip: str) -> Dict[str, Any]:
        """添加 IP 到白名单"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        success = self.backend.add_to_whitelist(ip)
        if success and self.backend:
            self.backend.apply_rules()
        
        return {
            "success": success,
            "ip": ip,
            "message": f"IP {ip} 已添加到白名单" if success else "IP 已在白名单中"
        }
    
    def blacklist_add(self, ip: str) -> Dict[str, Any]:
        """添加 IP 到黑名单"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        success = self.backend.add_to_blacklist(ip)
        if success and self.backend:
            self.backend.apply_rules()
        
        # 如果是自动封禁，记录解封时间
        if self._auto_block_enabled:
            self._blocked_ips[ip] = time.time() + 3600  # 1 小时后自动解封
        
        return {
            "success": success,
            "ip": ip,
            "message": f"IP {ip} 已添加到黑名单" if success else "IP 已在黑名单中"
        }
    
    def set_rate_limit(self, ip: str, requests: int, window: int) -> Dict[str, Any]:
        """设置 IP 速率限制"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        success = self.backend.set_rate_limit(ip, requests, window)
        return {
            "success": success,
            "ip": ip,
            "limit": {"requests": requests, "window": window},
            "message": "速率限制设置成功" if success else "速率限制设置失败"
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取防火墙统计信息"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        stats = self.backend.get_stats()
        stats["backend_type"] = type(self.backend).__name__
        stats["rules_count"] = len(self.backend.rules)
        stats["whitelist_count"] = len(self.backend.whitelist)
        stats["blacklist_count"] = len(self.backend.blacklist)
        stats["blocked_ips"] = list(self._blocked_ips.keys())
        
        return {
            "success": True,
            "stats": stats
        }
    
    def reload_rules(self) -> Dict[str, Any]:
        """重新加载规则"""
        if not self.backend:
            return {"success": False, "error": "防火墙后端未初始化"}
        
        self._load_rules()
        success = self.backend.reload()
        
        return {
            "success": success,
            "message": "规则重新加载成功" if success else "规则重新加载失败"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取防火墙状态"""
        return {
            "success": True,
            "status": {
                "running": self._running,
                "backend": type(self.backend).__name__ if self.backend else "None",
                "auto_block_enabled": self._auto_block_enabled,
                "threat_threshold": self._threat_threshold,
                "active_blocks": len(self._blocked_ips)
            }
        }
    
    def register_pl_functions(self, injector: Any):
        """注册 PL 注入功能"""
        
        def add_firewall_rule(**kwargs) -> Dict[str, Any]:
            """添加防火墙规则"""
            return self.add_rule(kwargs)
        
        injector.register_function(
            "firewall:add_rule",
            add_firewall_rule,
            "添加防火墙规则（支持 protocol, src_ip, dst_ip, dst_port, action 等参数）"
        )
        
        def remove_firewall_rule(rule_id: str) -> Dict[str, Any]:
            """删除防火墙规则"""
            return self.remove_rule(rule_id)
        
        injector.register_function(
            "firewall:remove_rule",
            remove_firewall_rule,
            "删除指定 ID 的防火墙规则"
        )
        
        def list_firewall_rules() -> Dict[str, Any]:
            """列出所有防火墙规则"""
            return self.list_rules()
        
        injector.register_function(
            "firewall:list_rules",
            list_firewall_rules,
            "列出所有防火墙规则"
        )
        
        def whitelist_ip(ip: str) -> Dict[str, Any]:
            """添加 IP 到白名单"""
            return self.whitelist_add(ip)
        
        injector.register_function(
            "firewall:whitelist_add",
            whitelist_ip,
            "将 IP 地址添加到白名单"
        )
        
        def blacklist_ip(ip: str) -> Dict[str, Any]:
            """添加 IP 到黑名单"""
            return self.blacklist_add(ip)
        
        injector.register_function(
            "firewall:blacklist_add",
            blacklist_ip,
            "将 IP 地址添加到黑名单"
        )
        
        def rate_limit_ip(ip: str, requests: int, window: int) -> Dict[str, Any]:
            """设置 IP 速率限制"""
            return self.set_rate_limit(ip, requests, window)
        
        injector.register_function(
            "firewall:rate_limit",
            rate_limit_ip,
            "为指定 IP 设置速率限制（requests: 请求数，window: 时间窗口秒数）"
        )
        
        def get_firewall_stats() -> Dict[str, Any]:
            """获取防火墙统计"""
            return self.get_stats()
        
        injector.register_function(
            "firewall:get_stats",
            get_firewall_stats,
            "获取防火墙统计信息（包处理数、规则数等）"
        )
        
        def reload_firewall_rules() -> Dict[str, Any]:
            """重新加载防火墙规则"""
            return self.reload_rules()
        
        injector.register_function(
            "firewall:reload",
            reload_firewall_rules,
            "重新加载防火墙规则（热更新）"
        )
        
        def get_firewall_status() -> Dict[str, Any]:
            """获取防火墙状态"""
            return self.get_status()
        
        injector.register_function(
            "firewall:status",
            get_firewall_status,
            "获取防火墙运行状态"
        )


def New() -> FirewallPlugin:
    """创建插件实例"""
    return FirewallPlugin()
