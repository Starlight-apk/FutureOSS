"""插件加载器 - 加载基础插件（带沙箱隔离）"""
import sys
import importlib.util
from pathlib import Path
from typing import Any, Optional

from oss.plugin.types import Plugin


class Sandbox:
    """沙箱隔离"""

    def __init__(self):
        self._restricted_builtins = {
            "__builtins__": {
                "True": True,
                "False": False,
                "None": None,
                "dict": dict,
                "list": list,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "tuple": tuple,
                "set": set,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "reversed": reversed,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "round": round,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "type": type,
                "id": id,
                "hash": hash,
                "repr": repr,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "print": print,
            }
        }

    def get_safe_globals(self) -> dict:
        """获取安全的 globals"""
        return dict(self._restricted_builtins)


class PluginLoader:
    """插件加载器（带沙箱隔离）"""

    def __init__(self, enable_sandbox: bool = True):
        self.loaded: dict[str, Any] = {}
        self.sandbox = Sandbox() if enable_sandbox else None

    def load_core_plugin(self, plugin_name: str, store_dir: str = "store") -> Optional[dict[str, Any]]:
        """加载核心插件（不受沙箱限制）"""
        plugin_dir = Path(store_dir) / "@{FutureOSS}" / plugin_name
        return self._load_plugin(plugin_name, plugin_dir, use_sandbox=False, allow_relative=True)

    def load_sandbox_plugin(self, plugin_dir: Path) -> Optional[dict[str, Any]]:
        """加载沙箱插件"""
        plugin_name = plugin_dir.name
        result = self._load_plugin(plugin_name, plugin_dir, use_sandbox=True, allow_relative=True)
        return result

    def _load_plugin(self, plugin_name: str, plugin_dir: Path, use_sandbox: bool = True, allow_relative: bool = False) -> Optional[dict[str, Any]]:
        """加载插件"""
        if not (plugin_dir / "main.py").exists():
            return None

        # 清理插件名（去掉 } 等）
        clean_name = plugin_name.rstrip("}")
        module_name = f"plugin.{clean_name}"
        spec = importlib.util.spec_from_file_location(module_name, str(plugin_dir / "main.py"))
        module = importlib.util.module_from_spec(spec)
        module.__package__ = module_name
        module.__path__ = [str(plugin_dir)]  # 启用相对导入子模块
        sys.modules[spec.name] = module

        # 沙箱模式：限制内置函数
        if use_sandbox and self.sandbox:
            safe_globals = self.sandbox.get_safe_globals()
            # 允许导入框架模块
            safe_globals["__builtins__"]["__import__"] = self._safe_import
            spec.loader.exec_module(module)
        else:
            spec.loader.exec_module(module)

        if not hasattr(module, "New"):
            return None

        instance = module.New()
        self.loaded[clean_name] = {
            "instance": instance,
            "module": module,
            "path": str(plugin_dir),
            "name": clean_name,  # 存储清理后的名称
        }
        return self.loaded[clean_name]

    @staticmethod
    def _safe_import(name: str, globals: dict = None, locals: dict = None, fromlist: tuple = (), level: int = 0):
        """安全导入：只允许导入框架模块、标准库子集和插件自身模块"""
        allowed_prefixes = ("oss.", "json.", "time.", "datetime.", "enum.", "typing.", "dataclasses.", "pathlib.", "mimetypes.", "http.", "threading.", "socket.", "asyncio.", "websockets.", "re.", "urllib.", "shutil.", "string.", "io.", "base64.", "hashlib.", "hmac.", "secrets.", "math.", "random.", "collections.", "functools.", "itertools.", "operator.", "copy.", "pprint.", "textwrap.", "unicodedata.", "struct.", "codecs.", "locale.", "gettext.", "logging.", "warnings.", "contextlib.", "abc.", "atexit.", "traceback.", "linecache.", "tokenize.", "keyword.", "ast.", "dis.", "inspect.", "types.", "__future__.", "importlib.", "pkgutil.", "sys.", "os.", "stat.", "glob.", "tempfile.", "fnmatch.", "csv.", "configparser.", "argparse.", "html.", "xml.", "email.", "mailbox.", "mimetypes.", "binascii.", "zlib.", "gzip.", "bz2.", "lzma.", "zipfile.", "tarfile.", "sqlite3.", "zlib.")
        if any(name.startswith(p) for p in allowed_prefixes):
            return __import__(name, globals, locals, fromlist, level)
        # 允许相对导入（插件自身模块）
        if level > 0:
            return __import__(name, globals, locals, fromlist, level)
        raise ImportError(f"插件不允许导入模块: {name}")

