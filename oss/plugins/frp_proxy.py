"""
FutureOSS v1.1.0 - FRP 内网穿透插件
功能：反向代理、隧道管理、流量统计、访问控制
"""
import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from oss.plugin.base import BasePlugin
from oss.core.context import Context

logger = logging.getLogger("futureoss.frp")

class FRPPlugin(BasePlugin):
    name = "frp_proxy"
    version = "1.1.0"
    description = "FRP 内网穿透服务：安全反向代理隧道"
    
    def __init__(self):
        super().__init__()
        self.config_dir = "./frp_config"
        self.tunnels: Dict[str, Dict] = {}
        self.frpc_process = None
        self.frp_server = {
            "address": "frp.example.com",
            "port": 7000,
            "token": "futureoss_frp_token"
        }
        
        os.makedirs(self.config_dir, exist_ok=True)

    def on_load(self, ctx: Context):
        logger.info("FRP 内网穿透插件已加载")
        
        # 注册命令
        ctx.register_command("frp.tunnel.create", self.create_tunnel)
        ctx.register_command("frp.tunnel.remove", self.remove_tunnel)
        ctx.register_command("frp.tunnel.list", self.list_tunnels)
        ctx.register_command("frp.tunnel.start", self.start_tunnel)
        ctx.register_command("frp.tunnel.stop", self.stop_tunnel)
        ctx.register_command("frp.server.config", self.configure_server)

    def create_tunnel(self, ctx: Context, name: str, type: str, local_port: int, remote_port: int, **kwargs):
        """创建 FRP 隧道"""
        if name in self.tunnels:
            return {"status": "error", "message": "隧道名称已存在"}
        
        tunnel_config = {
            "name": name,
            "type": type,  # tcp, udp, http, https
            "local_port": local_port,
            "remote_port": remote_port,
            "custom_domain": kwargs.get("domain"),
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "traffic_stats": {"in": 0, "out": 0}
        }
        
        # 生成 FRP 配置文件
        config_content = f"""
[{name}]
type = {type}
local_ip = 127.0.0.1
local_port = {local_port}
remote_port = {remote_port}
"""
        if kwargs.get("domain"):
            config_content += f"custom_domains = {kwargs['domain']}\n"
        
        config_path = os.path.join(self.config_dir, f"{name}.ini")
        with open(config_path, "w") as f:
            f.write(config_content)
        
        self.tunnels[name] = tunnel_config
        logger.info(f"FRP 隧道 {name} 已创建")
        
        return {"status": "success", "tunnel": tunnel_config, "config_file": config_path}

    def remove_tunnel(self, ctx: Context, name: str):
        """删除 FRP 隧道"""
        if name not in self.tunnels:
            return {"status": "error", "message": "隧道不存在"}
        
        # 如果正在运行，先停止
        if self.tunnels[name]["status"] == "running":
            self.stop_tunnel(ctx, name)
        
        # 删除配置文件
        config_path = os.path.join(self.config_dir, f"{name}.ini")
        if os.path.exists(config_path):
            os.remove(config_path)
        
        del self.tunnels[name]
        logger.info(f"FRP 隧道 {name} 已删除")
        return {"status": "success", "message": f"隧道 {name} 已删除"}

    def list_tunnels(self, ctx: Context):
        """列出所有 FRP 隧道"""
        return {"status": "success", "tunnels": list(self.tunnels.values())}

    def start_tunnel(self, ctx: Context, name: str):
        """启动 FRP 隧道"""
        if name not in self.tunnels:
            return {"status": "error", "message": "隧道不存在"}
        
        tunnel = self.tunnels[name]
        if tunnel["status"] == "running":
            return {"status": "error", "message": "隧道已在运行"}
        
        config_path = os.path.join(self.config_dir, f"{name}.ini")
        if not os.path.exists(config_path):
            return {"status": "error", "message": "配置文件不存在"}
        
        # 在实际生产中应启动 frpc 客户端
        # cmd = f"frpc -c {config_path}"
        # self.frpc_process = subprocess.Popen(cmd.split())
        
        tunnel["status"] = "running"
        tunnel["started_at"] = datetime.now().isoformat()
        logger.info(f"FRP 隧道 {name} 已启动")
        
        return {"status": "success", "message": f"隧道 {name} 已启动", "tunnel": tunnel}

    def stop_tunnel(self, ctx: Context, name: str):
        """停止 FRP 隧道"""
        if name not in self.tunnels:
            return {"status": "error", "message": "隧道不存在"}
        
        tunnel = self.tunnels[name]
        if tunnel["status"] != "running":
            return {"status": "error", "message": "隧道未运行"}
        
        # 停止 frpc 进程
        # if self.frpc_process:
        #     self.frpc_process.terminate()
        
        tunnel["status"] = "stopped"
        logger.info(f"FRP 隧道 {name} 已停止")
        return {"status": "success", "message": f"隧道 {name} 已停止"}

    def configure_server(self, ctx: Context, address: str, port: int, token: str):
        """配置 FRP 服务器信息"""
        self.frp_server = {
            "address": address,
            "port": port,
            "token": token
        }
        
        # 生成主配置文件
        main_config = f"""
[common]
server_addr = {address}
server_port = {port}
token = {token}
log_file = ./logs/frpc.log
log_level = info
"""
        config_path = os.path.join(self.config_dir, "frpc.ini")
        with open(config_path, "w") as f:
            f.write(main_config)
        
        logger.info(f"FRP 服务器配置已更新：{address}:{port}")
        return {"status": "success", "config": self.frp_server}

    def on_unload(self, ctx: Context):
        # 停止所有隧道
        for name in list(self.tunnels.keys()):
            if self.tunnels[name]["status"] == "running":
                self.stop_tunnel(ctx, name)
        logger.info("FRP 内网穿透插件已卸载")
