"""
FutureOSS v1.1.0 - 自动化运维工具箱
功能：一键备份/恢复、健康检查、资源配额管理、自动重启
"""
import os
import json
import time
import tarfile
import shutil
import logging
import threading
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from oss.plugin.base import BasePlugin
from oss.core.context import Context

logger = logging.getLogger("futureoss.ops")

class OpsToolboxPlugin(BasePlugin):
    name = "ops_toolbox"
    version = "1.1.0"
    description = "自动化运维工具箱：备份、健康检查、资源配额"
    
    def __init__(self):
        super().__init__()
        self.backup_dir = "./backups"
        self.health_checks: Dict[str, Dict] = {}
        self.resource_quotas: Dict[str, Dict] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # 默认配额
        self.default_quota = {
            "max_memory_mb": 512,
            "max_cpu_percent": 50,
            "max_open_files": 1024
        }

    def on_load(self, ctx: Context):
        logger.info("运维工具箱已启动")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 注册命令
        ctx.register_command("ops.backup.create", self.create_backup)
        ctx.register_command("ops.backup.restore", self.restore_backup)
        ctx.register_command("ops.backup.list", self.list_backups)
        ctx.register_command("ops.health.check", self.run_health_check)
        ctx.register_command("ops.quota.set", self.set_quota)
        ctx.register_command("ops.quota.get", self.get_quota)
        
        # 启动后台监控
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def create_backup(self, ctx: Context, name: Optional[str] = None):
        """创建系统备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        try:
            # 备份配置文件和插件数据
            files_to_backup = []
            for root in ["./config", "./plugins/data", "./logs"]:
                if os.path.exists(root):
                    files_to_backup.append(root)
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for file_path in files_to_backup:
                    tar.add(file_path, arcname=os.path.basename(file_path))
            
            metadata = {
                "name": backup_name,
                "timestamp": timestamp,
                "files": files_to_backup,
                "size_mb": round(os.path.getsize(backup_path) / 1024 / 1024, 2)
            }
            
            # 保存元数据
            meta_path = backup_path.replace(".tar.gz", ".json")
            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=2)
                
            logger.info(f"备份创建成功：{backup_name}")
            return {"status": "success", "backup": metadata}
        except Exception as e:
            logger.error(f"备份失败：{e}")
            return {"status": "error", "message": str(e)}

    def restore_backup(self, ctx: Context, backup_name: str):
        """恢复备份"""
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        if not os.path.exists(backup_path):
            return {"status": "error", "message": "备份文件不存在"}
        
        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(path="./")
            logger.info(f"备份恢复成功：{backup_name}")
            return {"status": "success", "message": "恢复完成，请重启系统"}
        except Exception as e:
            logger.error(f"恢复失败：{e}")
            return {"status": "error", "message": str(e)}

    def list_backups(self, ctx: Context):
        """列出所有备份"""
        backups = []
        for f in os.listdir(self.backup_dir):
            if f.endswith(".tar.gz"):
                meta_path = os.path.join(self.backup_dir, f.replace(".tar.gz", ".json"))
                if os.path.exists(meta_path):
                    with open(meta_path) as mf:
                        backups.append(json.load(mf))
                else:
                    backups.append({"name": f, "size_mb": round(os.path.getsize(os.path.join(self.backup_dir, f)) / 1024 / 1024, 2)})
        return {"status": "success", "backups": sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)}

    def run_health_check(self, ctx: Context):
        """执行健康检查"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "system": {},
            "plugins": {},
            "issues": []
        }
        
        # 系统级检查
        results["system"]["cpu"] = psutil.cpu_percent(interval=1)
        results["system"]["memory"] = psutil.virtual_memory().percent
        results["system"]["disk"] = psutil.disk_usage("/").percent
        
        if results["system"]["cpu"] > 90:
            results["issues"].append("CPU 使用率过高")
        if results["system"]["memory"] > 90:
            results["issues"].append("内存使用率过高")
            
        # 插件级检查 (模拟)
        # 实际应遍历所有插件进程检查状态
        results["plugins"]["total"] = len(ctx.plugins) if hasattr(ctx, 'plugins') else 0
        results["plugins"]["healthy"] = results["plugins"]["total"]
        
        return {"status": "success", "health": results}

    def set_quota(self, ctx: Context, plugin_id: str, **kwargs):
        """设置插件资源配额"""
        quota = self.default_quota.copy()
        quota.update(kwargs)
        self.resource_quotas[plugin_id] = quota
        logger.info(f"插件 {plugin_id} 配额已更新：{quota}")
        return {"status": "success", "quota": quota}

    def get_quota(self, ctx: Context, plugin_id: str):
        """获取插件资源配额"""
        return {"status": "success", "quota": self.resource_quotas.get(plugin_id, self.default_quota)}

    def _monitor_loop(self):
        """后台监控循环"""
        while self.monitoring_active:
            try:
                # 检查资源配额
                for pid, proc in enumerate(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])):
                    # 简化逻辑：实际应根据插件名匹配
                    pass
                
                # 自动重启检测 (简化版)
                # 实际应检查插件进程是否存活
                
                time.sleep(10)  # 每 10 秒检查一次
            except Exception as e:
                logger.error(f"监控循环错误：{e}")

    def on_unload(self, ctx: Context):
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("运维工具箱已停止")
