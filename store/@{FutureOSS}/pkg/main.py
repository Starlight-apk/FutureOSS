"""包管理插件 - 搜索、安装、卸载、更新插件"""
import os
import json
import shutil
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Optional

from oss.logger.logger import Log
from oss.plugin.types import Plugin, register_plugin_type


# 远程仓库地址（可配置）
# 插件存储在 future-oss 仓库的 store/ 目录下
DEFAULT_REGISTRY = "https://gitee.com/starlight-apk/future-oss/raw/main"

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
        # 扫描 @{author}/plugin_name 结构
        for author_dir in PKG_DIR.iterdir():
            if author_dir.is_dir() and author_dir.name.startswith("@{"):
                for plugin_dir in author_dir.iterdir():
                    if plugin_dir.is_dir():
                        manifest = plugin_dir / "manifest.json"
                        if manifest.exists():
                            with open(manifest, "r", encoding="utf-8") as f:
                                full_name = author_dir.name + "/" + plugin_dir.name
                                self.installed[full_name] = json.load(f)

    def search(self, query: str = "") -> list[PackageInfo]:
        """搜索可用的包"""
        # 简化版本：直接返回本地缓存
        # 实际使用时可以通过 API 或配置文件维护一个插件索引
        return self._search_from_cache(query)
    
    def _search_from_cache(self, query: str = "") -> list[PackageInfo]:
        """从本地缓存搜索包"""
        results = []
        for pkg_name, pkg_info in self.index_cache.items():
            if not query or query.lower() in pkg_name.lower() or query.lower() in pkg_info.get("description", "").lower():
                results.append(pkg_info)
        return results

    def install(self, name: str, version: str = "") -> bool:
        """安装包，支持 @{作者名称}/插件名称 格式"""
        # 解析输入格式 @{author}/plugin 或直接插件名
        author = "FutureOSS"  # 默认作者
        plugin_name = name

        if name.startswith("@{") and "}/" in name:
            # 解析 @{author}/plugin 格式
            end_bracket = name.index("}/")
            author = name[2:end_bracket]
            plugin_name = name[end_bracket + 2:]
        elif name.startswith("@{") and name.endswith("}") and "/" in name:
            # 兼容旧格式 @{author/plugin}
            inner = name[2:-1]
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
            # 插件存储在 store/@{author}/plugin_name 目录下
            pkg_info = PackageInfo()
            pkg_info.name = plugin_name
            pkg_info.author = author
            pkg_info.version = version or "1.0.0"
            pkg_info.download_url = f"{self.registry}/store/@{{{author}}}/{plugin_name}"

        # 创建安装目录 @{author}/plugin_name
        install_dir = PKG_DIR / ("@{" + author + "}") / plugin_name
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
            full_name = "@{" + author + "}/" + plugin_name
            self.installed[full_name] = manifest_data
            Log.info("pkg", f"已安装: {full_name} {manifest_data.get('metadata', {}).get('version', '')}")
            return True
        except Exception as e:
            Log.error("pkg", f"安装失败 {name}: {e}")
            # 清理失败的安装
            if install_dir.exists():
                shutil.rmtree(install_dir)
            return False

    def uninstall(self, name: str) -> bool:
        """卸载包，支持 @{作者名称}/插件名称 格式"""
        # 解析格式获取目录路径
        if name.startswith("@{") and "}/" in name:
            end_bracket = name.index("}/")
            author = name[2:end_bracket]
            plugin_name = name[end_bracket + 2:]
            install_dir = PKG_DIR / ("@{" + author + "}") / plugin_name
        elif name.startswith("@{") and name.endswith("}") and "/" in name:
            # 兼容旧格式
            install_dir = PKG_DIR / name
        else:
            install_dir = PKG_DIR / name

        if not install_dir.exists():
            Log.info("pkg", f"包未安装: {name}")
            return False

        try:
            shutil.rmtree(install_dir)
            # 从已安装列表中移除
            for key in list(self.installed.keys()):
                if key == name or key.endswith("/" + install_dir.name):
                    del self.installed[key]
                    break
            Log.info("pkg", f"已卸载: {name}")
            return True
        except Exception as e:
            Log.error("pkg", f"卸载失败 {name}: {e}")
            return False

    def update(self, name: str = "") -> bool:
        """更新包"""
        if name:
            # 更新单个包
            if name not in self.installed:
                Log.info("pkg", f"包未安装: {name}")
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
        Log.info("pkg", "包管理器已初始化")

    def start(self):
        """启动"""
        Log.info("pkg", f"包管理器已启动，已安装 {len(self.manager.installed)} 个包")

    def stop(self):
        """停止"""
        pass


# 注册类型
register_plugin_type("PackageManager", PackageManager)
register_plugin_type("PackageInfo", PackageInfo)


def New():
    return PkgPlugin()
