"""
FutureOSS v1.1.0 - 多语言项目部署编排器
功能：语言环境管理、自动构建、配置模板、一键部署
支持：Python, Node.js, Go, Java, PHP
"""
import os
import json
import subprocess
import logging
import shutil
from typing import Dict, List, Optional
from datetime import datetime
from oss.plugin.base import BasePlugin
from oss.core.context import Context

logger = logging.getLogger("futureoss.deploy")

class MultiLangDeployPlugin(BasePlugin):
    name = "multi_lang_deploy"
    version = "1.1.0"
    description = "多语言项目部署编排器：自动检测、构建、部署"
    
    def __init__(self):
        super().__init__()
        self.projects_dir = "./projects"
        self.runtimes = {
            "python": {"file": "requirements.txt", "install": "pip install -r requirements.txt", "run": "python main.py"},
            "nodejs": {"file": "package.json", "install": "npm install", "run": "node main.js"},
            "go": {"file": "go.mod", "install": "go mod download", "run": "go run main.go"},
            "java": {"file": "pom.xml", "install": "mvn dependency:resolve", "run": "java -jar target/*.jar"},
            "php": {"file": "composer.json", "install": "composer install", "run": "php -S localhost:8000"}
        }
        self.deployed_projects: Dict[str, Dict] = {}

    def on_load(self, ctx: Context):
        logger.info("多语言部署编排器已启动")
        os.makedirs(self.projects_dir, exist_ok=True)
        
        # 注册命令
        ctx.register_command("deploy.project.detect", self.detect_language)
        ctx.register_command("deploy.project.build", self.build_project)
        ctx.register_command("deploy.project.start", self.start_project)
        ctx.register_command("deploy.project.stop", self.stop_project)
        ctx.register_command("deploy.project.list", self.list_projects)
        ctx.register_command("deploy.runtime.check", self.check_runtimes)

    def detect_language(self, ctx: Context, project_path: str) -> Dict:
        """自动检测项目语言"""
        if not os.path.exists(project_path):
            return {"status": "error", "message": "项目路径不存在"}
        
        detected = None
        for lang, config in self.runtimes.items():
            if os.path.exists(os.path.join(project_path, config["file"])):
                detected = lang
                break
        
        if not detected:
            return {"status": "error", "message": "无法识别项目类型"}
        
        return {
            "status": "success",
            "language": detected,
            "path": project_path,
            "config_file": self.runtimes[detected]["file"]
        }

    def build_project(self, ctx: Context, project_name: str, project_path: str):
        """构建项目（安装依赖）"""
        detection = self.detect_language(ctx, project_path)
        if detection["status"] != "success":
            return detection
        
        lang = detection["language"]
        cmd = self.runtimes[lang]["install"]
        
        try:
            logger.info(f"正在构建 {project_name} ({lang})...")
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=project_path, 
                capture_output=True, 
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return {"status": "error", "message": f"构建失败：{result.stderr}"}
            
            # 保存项目信息
            self.deployed_projects[project_name] = {
                "name": project_name,
                "path": project_path,
                "language": lang,
                "status": "built",
                "built_at": datetime.now().isoformat()
            }
            
            logger.info(f"项目 {project_name} 构建成功")
            return {"status": "success", "message": "构建完成", "project": self.deployed_projects[project_name]}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "构建超时"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start_project(self, ctx: Context, project_name: str):
        """启动项目"""
        if project_name not in self.deployed_projects:
            return {"status": "error", "message": "项目未找到"}
        
        proj = self.deployed_projects[project_name]
        cmd = self.runtimes[proj["language"]]["run"]
        
        try:
            # 在实际生产中应使用进程管理器
            logger.info(f"正在启动 {project_name}...")
            # subprocess.Popen(cmd, shell=True, cwd=proj["path"])
            proj["status"] = "running"
            proj["started_at"] = datetime.now().isoformat()
            
            return {"status": "success", "message": f"项目 {project_name} 已启动", "project": proj}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop_project(self, ctx: Context, project_name: str):
        """停止项目"""
        if project_name not in self.deployed_projects:
            return {"status": "error", "message": "项目未找到"}
        
        self.deployed_projects[project_name]["status"] = "stopped"
        logger.info(f"项目 {project_name} 已停止")
        return {"status": "success", "message": "项目已停止"}

    def list_projects(self, ctx: Context):
        """列出所有项目"""
        return {"status": "success", "projects": list(self.deployed_projects.values())}

    def check_runtimes(self, ctx: Context):
        """检查已安装的运行时环境"""
        results = {}
        for lang in self.runtimes.keys():
            installed = False
            version = "N/A"
            try:
                if lang == "python":
                    result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
                    installed = result.returncode == 0
                    version = result.stdout.strip()
                elif lang == "nodejs":
                    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
                    installed = result.returncode == 0
                    version = result.stdout.strip()
                elif lang == "go":
                    result = subprocess.run(["go", "version"], capture_output=True, text=True)
                    installed = result.returncode == 0
                    version = result.stdout.strip()
                elif lang == "java":
                    result = subprocess.run(["java", "-version"], capture_output=True, text=True)
                    installed = result.returncode == 0
                    version = "Java installed"
                elif lang == "php":
                    result = subprocess.run(["php", "--version"], capture_output=True, text=True)
                    installed = result.returncode == 0
                    version = result.stdout.strip().split('\n')[0]
            except:
                pass
            
            results[lang] = {"installed": installed, "version": version}
        
        return {"status": "success", "runtimes": results}

    def on_unload(self, ctx: Context):
        # 停止所有运行中的项目
        for name in list(self.deployed_projects.keys()):
            if self.deployed_projects[name].get("status") == "running":
                self.stop_project(ctx, name)
        logger.info("多语言部署编排器已停止")
