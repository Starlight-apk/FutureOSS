
    def __init__(self, plugin_name: str, data_dir: str = None):
        config = get_config()
        self.plugin_name = plugin_name
        self.data_dir = Path(data_dir or str(config.data_dir)) / plugin_name
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._load()


    def _load(self):
        data_file = self.data_dir / "data.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            self._data[key] = value
            self._save()

    def delete(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def keys(self) -> list[str]:
        with self._lock:
            self._data.clear()
            self._save()

    def size(self) -> int:
        with self._lock:
            return self._data.copy()

    def set_many(self, data: dict[str, Any]):
        return {
            "plugin": self.plugin_name,
            "keys": self.size(),
            "path": str(self.data_dir),
        }


    def read_file(self, path: str, mode: str = "r") -> Optional[str | bytes]:
        try:
            file_path = self._resolve_path(path)
            if not file_path.exists() or not file_path.is_file():
                return None
            with open(file_path, mode, encoding="utf-8" if mode == "r" else None) as f:
                return f.read()
        except Exception as e:
            Log.error("plugin-storage", f"读取文件失败 {self.plugin_name}/{path}: {type(e).__name__}: {e}")
            return None

    def write_file(self, path: str, content: str | bytes):
        try:
            file_path = self._resolve_path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                with open(file_path, "wb") as f:
                    f.write(content)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            Log.error("plugin-storage", f"写入文件失败 {self.plugin_name}/{path}: {type(e).__name__}: {e}")

    def delete_file(self, path: str) -> bool:
        
        Args:
            prefix: 子目录前缀，如 "templates/" 或 ""（全部）
        
        Returns:
            相对路径列表
        try:
            search_dir = self._resolve_path(prefix) if prefix else self.data_dir
            if not search_dir.exists():
                return []
            files = []
            for f in search_dir.rglob("*"):
                if f.is_file():
                    files.append(str(f.relative_to(self.data_dir)))
            return sorted(files)
        except Exception as e:
            Log.error("plugin-storage", f"列出文件失败：{type(e).__name__}: {e}")
            return []

    def file_exists(self, path: str) -> bool:
        
        用于插件向外部提供静态文件。
        自动检测 MIME 类型，支持文本和二进制文件。
        
        Args:
            path: 相对于插件数据目录的路径
        
        Returns:
            Response 对象（200 成功 / 404 不存在 / 403 安全拦截）
        try:
            file_path = self._resolve_path(path)
            
            try:
                file_path.resolve().relative_to(self.data_dir.resolve())
            except ValueError:
                return Response(status=403, body="Forbidden: path traversal detected")

            if not file_path.exists() or not file_path.is_file():
                return Response(status=404, body=f"File not found: {path}")

            content_type, _ = mimetypes.guess_type(str(file_path))
            if not content_type:
                content_type = "application/octet-stream"

            if content_type.startswith("text/") or content_type in (
                "application/json", "application/javascript", "application/xml",
                "text/css", "text/html", "image/svg+xml"
            ):
                content = file_path.read_text(encoding="utf-8")
            else:
                content = file_path.read_bytes()

            return Response(
                status=200,
                headers={
                    "Content-Type": content_type,
                    "Cache-Control": "public, max-age=3600",
                },
                body=content,
            )
        except Exception as e:
            return Response(status=500, body=f"Error serving file: {e}")

    def _resolve_path(self, path: str) -> Path:
        return self.data_dir.resolve()


class SharedStorage:
        return self._manager.get_storage(plugin_name)

    def get_shared(self, key: str, default: Any = None) -> Any:
        shared_file = self._shared_dir / f"{key}.json"
        with open(shared_file, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)

    def list_storages(self) -> list[str]:

    def __init__(self):
        self.storages: dict[str, PluginStorage] = {}
        self.shared = None
        self.config = {}
        self.data_root = Path("./data")

    def init(self, deps: dict = None):
        Log.info("plugin-storage", f"插件存储服务已启动 (root={self.data_root})")

    def stop(self):
        config_path = Path("./data/plugin-storage/config.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            self.data_root = Path(self.config.get("data_root", "./data"))
            shared_dir_name = self.config.get("shared_dir", "DCIM")
            shared_dir = self.data_root / shared_dir_name
        else:
            Log.warn("plugin-storage", "config.json 不存在，使用默认配置")
            self.config = {"data_root": "./data", "shared_dir": "DCIM"}
            self.data_root = Path("./data")
            shared_dir = self.data_root / "DCIM"

        self.shared = SharedStorage(self, shared_dir=shared_dir)

    def get_storage(self, plugin_name: str) -> PluginStorage:
        if plugin_name in self.storages:
            del self.storages[plugin_name]
            data_dir = PluginStorage(plugin_name).data_dir
            if data_dir.exists():
                shutil.rmtree(data_dir)
            return True
        return False

    def list_storages(self) -> list[str]:
        return self.shared


register_plugin_type("PluginStorage", PluginStorage)
register_plugin_type("SharedStorage", SharedStorage)


def New():
    return PluginStoragePlugin()
