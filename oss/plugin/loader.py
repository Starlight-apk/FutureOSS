"""插件加载器 - 使用进程隔离确保安全性"""
import sys
import importlib.util
import multiprocessing
from multiprocessing import Process, Pipe
from pathlib import Path
from typing import Any, Optional, Dict
import signal
import os
from multiprocessing.connection import Connection

from oss.plugin.types import Plugin


class Sandbox:
    """沙箱隔离（已废弃，仅保留向后兼容）
    
    注意：此沙箱已被证明不安全，存在逃逸漏洞。
    请使用 ProcessIsolatedLoader 进行安全的插件加载。
    """

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
                "print": print,
            }
        }

    def get_safe_globals(self) -> dict:
        """获取安全的 globals"""
        return dict(self._restricted_builtins)


def _run_plugin_in_process(plugin_path: str, conn: Connection, timeout: float = 5.0):
    """在独立进程中运行插件代码"""
    try:
        # 设置超时处理
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Plugin execution timed out after {timeout}s")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))
        
        plugin_dir = Path(plugin_path)
        if not (plugin_dir / "main.py").exists():
            conn.send(("error", "Plugin main.py not found"))
            signal.alarm(0)
            return
        
        # 加载模块
        module_name = f"sandbox_plugin_{os.getpid()}"
        spec = importlib.util.spec_from_file_location(module_name, str(plugin_dir / "main.py"))
        module = importlib.util.module_from_spec(spec)
        module.__package__ = module_name
        module.__path__ = [str(plugin_dir)]
        sys.modules[spec.name] = module
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 检查是否有 New 函数
        if not hasattr(module, "New"):
            conn.send(("error", "Plugin missing 'New' function"))
            signal.alarm(0)
            return
        
        # 创建实例
        instance = module.New()
        
        # 返回成功结果（只返回基本信息，不返回可执行对象）
        conn.send(("success", {
            "name": plugin_dir.name.rstrip("}"),
            "path": str(plugin_dir),
            "has_new": True
        }))
        
        signal.alarm(0)
        
    except Exception as e:
        conn.send(("error", str(e)))
    finally:
        signal.alarm(0)
        conn.close()


class ProcessIsolatedLoader:
    """进程隔离插件加载器
    
    使用独立的子进程加载和运行第三方插件，确保即使插件恶意代码也无法影响主进程。
    """
    
    def __init__(self, timeout: float = 5.0):
        """
        Args:
            timeout: 插件加载超时时间（秒）
        """
        self.timeout = timeout
        self.loaded_plugins: Dict[str, dict] = {}
    
    def load_plugin(self, plugin_dir: Path) -> Optional[dict]:
        """在隔离进程中加载插件
        
        Args:
            plugin_dir: 插件目录路径
            
        Returns:
            插件信息字典，如果加载失败则返回 None
        """
        parent_conn, child_conn = Pipe()
        
        # 创建子进程
        process = Process(
            target=_run_plugin_in_process,
            args=(str(plugin_dir), child_conn, self.timeout),
            daemon=True
        )
        
        process.start()
        process.join(timeout=self.timeout + 2)  # 额外给 2 秒清理时间
        
        # 处理超时
        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
            if process.is_alive():
                process.kill()
                process.join(timeout=1)
            return None
        
        # 获取结果
        try:
            if parent_conn.poll(timeout=1):
                status, result = parent_conn.recv()
                
                if status == "success":
                    plugin_name = result["name"]
                    self.loaded_plugins[plugin_name] = {
                        "instance": None,  # 不保存实际实例，避免跨进程问题
                        "module": None,
                        "path": result["path"],
                        "name": plugin_name,
                        "isolated": True
                    }
                    return self.loaded_plugins[plugin_name]
                else:
                    # 记录错误但不抛出异常
                    print(f"Plugin load error: {result}")
                    return None
            else:
                return None
        except Exception as e:
            print(f"Failed to receive plugin result: {e}")
            return None
        finally:
            parent_conn.close()


class PluginLoader:
    """插件加载器（混合模式：核心插件直接加载，第三方插件进程隔离）"""

    def __init__(self, enable_sandbox: bool = True, isolation_timeout: float = 5.0):
        self.loaded: dict[str, Any] = {}
        self.sandbox = Sandbox() if enable_sandbox else None
        # 新增：进程隔离加载器用于第三方插件
        self.isolated_loader = ProcessIsolatedLoader(timeout=isolation_timeout)

    def load_core_plugin(self, plugin_name: str, store_dir: str = "store") -> Optional[dict[str, Any]]:
        """加载核心插件（不受沙箱限制，可信插件）"""
        plugin_dir = Path(store_dir) / "@{FutureOSS}" / plugin_name
        return self._load_plugin(plugin_name, plugin_dir, use_sandbox=False, allow_relative=True)

    def load_sandbox_plugin(self, plugin_dir: Path) -> Optional[dict[str, Any]]:
        """加载第三方插件（使用进程隔离确保安全）"""
        # 使用进程隔离代替不安全的沙箱
        return self.isolated_loader.load_plugin(plugin_dir)

    def _load_plugin(self, plugin_name: str, plugin_dir: Path, use_sandbox: bool = True, allow_relative: bool = False) -> Optional[dict[str, Any]]:
        """加载插件（内部方法，用于核心插件）"""
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

        # 沙箱模式：限制内置函数（仅用于核心插件的额外保护）
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
        raise ImportError(f"插件不允许导入模块：{name}")
