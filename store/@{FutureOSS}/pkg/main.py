"""包管理插件 - 搜索、安装、卸载、更新插件"""
import os
import json
import shutil
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Optional

from oss.plugin.types import Plugin, register_plugin_type


# 远程仓库地址（可配置）
DEFAULT_REGISTRY = "https://gitee.com/starlight-apk/future-oss-pkg/raw/main"

# 插件安装目录
PKG_DIR = Path("./data/pkg")


class PackageInfo:
    """包信息"""
    def __init__(self):
        self.name: str = ""
        self.version: str = ""
        self.author: str = ""
        self.description: str = ""
        self.download_url: str = ""
        self.dependencies: list[str] = []


class PackageManager:
    """包管理器"""

    def __init__(self):
        self.registry = DEFAULT_REGISTRY
        self.index_cache: dict[str, PackageInfo] = {}
        self.installed: dict[str, dict[str, Any]] = {}
        self._load_installed()

    def _load_installed(self):
        """加载已安装的包"""
        if not PKG_DIR.exists():
            return
        for pkg_dir in PKG_DIR.iterdir():
            if pkg_dir.is_dir():
                manifest = pkg_dir / "manifest.json"
                if manifest.exists():
                    with open(manifest, "r", encoding="utf-8") as f:
                        self.installed[pkg_dir.name] = json.load(f)

    def search(self, query: str = "") -> list[PackageInfo]:
        """搜索可用的包"""
        # 从远程仓库获取包索引
        index_url = f"{self.registry}/index.json"
        try:
            with urllib.request.urlopen(index_url, timeout=10) as resp:
                index = json.loads(resp.read().decode("utf-8"))
        except Exception:
            # 本地缓存
            return list(self.index_cache.values())

        results = []
        for pkg_name, pkg_info in index.items():
            if not query or query.lower() in pkg_name.lower() or query.lower() in pkg_info.get("description", "").lower():
                info = PackageInfo()
                info.name = pkg_name
                info.version = pkg_info.get("version", "")
                info.author = pkg_info.get("author", "")
                info.description = pkg_info.get("description", "")
                info.download_url = pkg_info.get("download_url", "")
                info.dependencies = pkg_info.get("dependencies", [])
                results.append(info)
                self.index_cache[pkg_name] = info

        return results

    def install(self, name: str, version: str = "") -> bool:
        """安装包，支持 @{作者/插件名} 格式"""
        # 解析输入格式 @{author/plugin} 或直接插件名
        author = "FutureOSS"  # 默认作者
        plugin_name = name
        
        if name.startswith("@{") and "/" in name:
            # 解析 @{author/plugin} 格式
            inner = name[2:-1] if name.endswith("}") else name[2:]
            parts = inner.split("/", 1)
            if len(parts) == 2:
                author, plugin_name = parts

        # 搜索获取下载链接
        packages = self.search(plugin_name)
        pkg_info = None
        for p in packages:
            if p.name == plugin_name and p.author == author:
                if not version or p.version == version:
                    pkg_info = p
                    break

        if not pkg_info or not pkg_info.download_url:
            # 尝试从远程仓库直接构建 URL
            pkg_info = PackageInfo()
            pkg_info.name = plugin_name
            pkg_info.author = author
            pkg_info.version = version or "1.0.0"
            pkg_info.download_url = self.registry + "/store/@{" + author + "/" + plugin_name + "}"

        # 创建安装目录 @{author/plugin_name}
        install_dir = PKG_DIR / ("@{" + author + "/" + plugin_name + "}")
        install_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 下载 manifest.json
            manifest_url = f"{pkg_info.download_url}/manifest.json"
            with urllib.request.urlopen(manifest_url, timeout=10) as resp:
                manifest_data = json.loads(resp.read().decode("utf-8"))
            with open(install_dir / "manifest.json", "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, ensure_ascii=False, indent=2)

            # 下载 main.py
            main_url = f"{pkg_info.download_url}/main.py"
            with urllib.request.urlopen(main_url, timeout=10) as resp:
                main_data = resp.read().decode("utf-8")
            with open(install_dir / "main.py", "w", encoding="utf-8") as f:
                f.write(main_data)

            # 更新已安装列表
            full_name = "@{" + author + "/" + plugin_name
            self.installed[full_name] = manifest_data
            print(f"[pkg] 已安装: {full_name} {manifest_data.get('metadata', {}).get('version', '')}")
            return True
        except Exception as e:
            print(f"[pkg] 安装失败 {name}: {e}")
            # 清理失败的安装
            if install_dir.exists():
                shutil.rmtree(install_dir)
            return False

    def uninstall(self, name: str) -> bool:
        """卸载包"""
        install_dir = PKG_DIR / name
        if not install_dir.exists():
            print(f"[pkg] 包未安装: {name}")
            return False

        try:
            shutil.rmtree(install_dir)
            del self.installed[name]
            print(f"[pkg] 已卸载: {name}")
            return True
        except Exception as e:
            print(f"[pkg] 卸载失败 {name}: {e}")
            return False

    def update(self, name: str = "") -> bool:
        """更新包"""
        if name:
            # 更新单个包
            if name not in self.installed:
                print(f"[pkg] 包未安装: {name}")
                return False
            return self.install(name)
        else:
            # 更新所有已安装的包
            success = True
            for pkg_name in list(self.installed.keys()):
                if not self.install(pkg_name):
                    success = False
            return success

    def list_installed(self) -> dict[str, Any]:
        """列出已安装的包"""
        return self.installed


class PkgPlugin(Plugin):
    """包管理插件"""

    def __init__(self):
        self.manager = PackageManager()

    def init(self, deps: dict = None):
        """初始化"""
        PKG_DIR.mkdir(parents=True, exist_ok=True)
        print("[pkg] 包管理器已初始化")

    def start(self):
        """启动"""
        print(f"[pkg] 包管理器已启动，已安装 {len(self.manager.installed)} 个包")

    def stop(self):
        """停止"""
        pass


# 注册类型
register_plugin_type("PackageManager", PackageManager)
register_plugin_type("PackageInfo", PackageInfo)


def New():
    return PkgPlugin()
