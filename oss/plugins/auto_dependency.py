"""
Auto Dependency Plugin - 依赖自动安装插件

该插件允许其他插件在声明文件 (manifest.json) 中声明所需的系统依赖，
然后扫描所有插件的声明文件，检查并安装缺失的系统依赖。

通过插件加载器的 /PL 注入能力接口进行对接。
"""

import json
import os
import subprocess
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

from oss.plugin.base import BasePlugin
from oss.core.context import Context


class AutoDependencyPlugin(BasePlugin):
    """依赖自动安装插件"""

    def __init__(self):
        super().__init__()
        self.name = "auto_dependency"
        self.version = "1.0.0"
        self.description = "自动扫描并安装插件声明的系统依赖"
        self.plugins_dir: Optional[Path] = None
        self.manifest_filename = "manifest.json"
        self.logger = None

    def init(self, deps: Optional[Dict[str, Any]] = None):
        """初始化插件"""
        # 获取插件目录路径
        self.plugins_dir = Path(__file__).parent
        if deps and 'logger' in deps:
            self.logger = deps['logger']
        else:
            import logging
            self.logger = logging.getLogger(self.name)
        
        self.logger.info(f"AutoDependencyPlugin 初始化完成，插件目录：{self.plugins_dir}")

    def start(self):
        """启动插件"""
        self.logger.info("AutoDependencyPlugin 启动")

    def stop(self):
        """停止插件"""
        self.logger.info("AutoDependencyPlugin 停止")

    def scan(self) -> List[Dict[str, Any]]:
        """
        扫描所有插件的声明文件，收集系统依赖信息
        
        Returns:
            List[Dict]: 包含所有插件依赖信息的列表
                每个元素格式: {
                    "plugin": str,           # 插件名称
                    "dependencies": List,    # 依赖列表
                    "package_manager": str   # 包管理器类型
                }
        """
        all_dependencies = []
        
        if not self.plugins_dir.exists():
            self.logger.warning(f"插件目录不存在: {self.plugins_dir}")
            return all_dependencies

        # 遍历所有插件文件
        for plugin_file in self.plugins_dir.glob("*.py"):
            plugin_name = plugin_file.stem
            
            # 跳过自身和__init__等文件
            if plugin_name.startswith("_") or plugin_name == self.name:
                continue
            
            # 查找对应的 manifest 文件
            manifest_path = self._find_manifest_for_plugin(plugin_name)
            
            if manifest_path and manifest_path.exists():
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    
                    # 提取系统依赖信息
                    system_deps = manifest.get("system_dependencies", [])
                    package_manager = manifest.get("package_manager", "apt-get")
                    
                    if system_deps:
                        all_dependencies.append({
                            "plugin": plugin_name,
                            "dependencies": system_deps,
                            "package_manager": package_manager,
                            "manifest_path": str(manifest_path)
                        })
                        
                        self.logger.info(
                            f"插件 {plugin_name} 声明了 {len(system_deps)} 个系统依赖"
                        )
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"解析 {manifest_path} 失败: {e}")
                except Exception as e:
                    self.logger.error(f"处理插件 {plugin_name} 时出错: {e}")

        return all_dependencies

    def check(self, dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        检查指定的系统依赖是否已安装
        
        Args:
            dependencies: 依赖信息列表，格式同 scan() 返回值
            
        Returns:
            Dict: 检查结果
                {
                    "total": int,              # 总依赖数
                    "installed": int,          # 已安装数
                    "missing": List[Dict],     # 缺失的依赖详情
                    "all_installed": bool      # 是否全部已安装
                }
        """
        result = {
            "total": 0,
            "installed": 0,
            "missing": [],
            "all_installed": True
        }
        
        for dep_info in dependencies:
            plugin_name = dep_info["plugin"]
            package_manager = dep_info["package_manager"]
            
            for package in dep_info["dependencies"]:
                result["total"] += 1
                
                if self._is_package_installed(package, package_manager):
                    result["installed"] += 1
                    self.logger.debug(f"包 {package} 已安装 (插件: {plugin_name})")
                else:
                    result["missing"].append({
                        "package": package,
                        "plugin": plugin_name,
                        "package_manager": package_manager
                    })
                    result["all_installed"] = False
                    self.logger.warning(f"包 {package} 未安装 (插件: {plugin_name})")

        return result

    def install(self, missing: List[Dict[str, str]], 
                auto_confirm: bool = True) -> Dict[str, Any]:
        """
        安装缺失的系统依赖
        
        Args:
            missing: 缺失的依赖列表，格式为 [{"package": str, "package_manager": str}]
            auto_confirm: 是否自动确认安装
            
        Returns:
            Dict: 安装结果
                {
                    "success": List[str],      # 成功安装的包
                    "failed": List[Dict],      # 安装失败的包及原因
                    "total": int,              # 尝试安装的总数
                }
        """
        result = {
            "success": [],
            "failed": [],
            "total": len(missing)
        }
        
        if not missing:
            self.logger.info("没有需要安装的依赖")
            return result

        # 按包管理器分组
        packages_by_pm: Dict[str, List[str]] = {}
        for item in missing:
            pm = item.get("package_manager", "apt-get")
            pkg = item["package"]
            
            if pm not in packages_by_pm:
                packages_by_pm[pm] = []
            packages_by_pm[pm].append(pkg)

        # 执行安装
        for pm, packages in packages_by_pm.items():
            self.logger.info(f"使用 {pm} 安装包: {', '.join(packages)}")
            
            success, failed = self._install_packages(packages, pm, auto_confirm)
            
            result["success"].extend(success)
            for fail_pkg, reason in failed:
                result["failed"].append({
                    "package": fail_pkg,
                    "reason": reason
                })

        return result

    def info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        Returns:
            Dict: 插件详细信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "supported_package_managers": [
                "apt-get", "yum", "dnf", "pacman", "brew", "apk"
            ],
            "api_methods": ["scan", "check", "install", "info"]
        }

    def _find_manifest_for_plugin(self, plugin_name: str) -> Optional[Path]:
        """查找插件对应的 manifest 文件"""
        # 可能的 manifest 文件位置
        possible_paths = [
            self.plugins_dir / f"{plugin_name}.json",
            self.plugins_dir / plugin_name / "manifest.json",
            self.plugins_dir / f"{plugin_name}" / f"{plugin_name}.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # 也检查插件文件同目录下的同名 json 文件
        plugin_file = self.plugins_dir / f"{plugin_name}.py"
        if plugin_file.exists():
            json_file = self.plugins_dir / f"{plugin_name}.json"
            if json_file.exists():
                return json_file
        
        return None

    def _is_package_installed(self, package: str, package_manager: str) -> bool:
        """检查包是否已安装"""
        try:
            if package_manager in ["apt-get", "apt"]:
                cmd = ["dpkg", "-l", package]
            elif package_manager in ["yum", "dnf"]:
                cmd = ["rpm", "-q", package]
            elif package_manager == "pacman":
                cmd = ["pacman", "-Q", package]
            elif package_manager == "brew":
                cmd = ["brew", "list", "--versions", package]
            elif package_manager == "apk":
                cmd = ["apk", "info", "-e", package]
            else:
                # 默认使用 which/whereis 检查可执行文件
                cmd = ["which", package]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"检查包 {package} 超时")
            return False
        except Exception as e:
            self.logger.error(f"检查包 {package} 时出错: {e}")
            return False

    def _install_packages(self, packages: List[str], 
                         package_manager: str,
                         auto_confirm: bool = True) -> tuple:
        """
        安装包
        
        Returns:
            tuple: (success_list, failed_list)
                success_list: 成功安装的包名列表
                failed_list: [(包名, 失败原因), ...]
        """
        success = []
        failed = []
        
        try:
            if package_manager in ["apt-get", "apt"]:
                cmd_prefix = ["apt-get", "install", "-y"] if auto_confirm else ["apt-get", "install"]
            elif package_manager == "yum":
                cmd_prefix = ["yum", "install", "-y"] if auto_confirm else ["yum", "install"]
            elif package_manager == "dnf":
                cmd_prefix = ["dnf", "install", "-y"] if auto_confirm else ["dnf", "install"]
            elif package_manager == "pacman":
                cmd_prefix = ["pacman", "-S", "--noconfirm"] if auto_confirm else ["pacman", "-S"]
            elif package_manager == "brew":
                cmd_prefix = ["brew", "install"]
            elif package_manager == "apk":
                cmd_prefix = ["apk", "add"]
            else:
                self.logger.error(f"不支持的包管理器: {package_manager}")
                for pkg in packages:
                    failed.append((pkg, f"不支持的包管理器: {package_manager}"))
                return success, failed

            # 合并命令
            cmd = cmd_prefix + packages
            
            self.logger.info(f"执行安装命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            if result.returncode == 0:
                success.extend(packages)
                self.logger.info(f"成功安装包: {', '.join(packages)}")
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                for pkg in packages:
                    failed.append((pkg, error_msg))
                self.logger.error(f"安装包失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            for pkg in packages:
                failed.append((pkg, "安装超时"))
            self.logger.error("安装包超时")
        except PermissionError:
            for pkg in packages:
                failed.append((pkg, "权限不足，需要 root 权限"))
            self.logger.error("安装包需要 root 权限")
        except Exception as e:
            for pkg in packages:
                failed.append((pkg, str(e)))
            self.logger.error(f"安装包时发生异常: {e}")

        return success, failed

    def execute(self, action: str, **kwargs) -> Any:
        """
        执行插件动作 (供插件加载器调用)
        
        Args:
            action: 动作名称 (scan, check, install, info)
            **kwargs: 动作参数
            
        Returns:
            动作执行结果
        """
        if action == "scan":
            return self.scan()
        elif action == "check":
            dependencies = kwargs.get("dependencies", self.scan())
            return self.check(dependencies)
        elif action == "install":
            missing = kwargs.get("missing", [])
            auto_confirm = kwargs.get("auto_confirm", True)
            return self.install(missing, auto_confirm)
        elif action == "info":
            return self.info()
        else:
            raise ValueError(f"未知的动作: {action}")
