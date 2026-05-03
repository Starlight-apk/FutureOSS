class HotReloadError(Exception):
    pass


class FileWatcher:
    def __init__(self, watch_dirs, extensions, callback):
        self.watch_dirs = watch_dirs
        self.extensions = extensions
        self.callback = callback
        self._running = False
        self._thread = None
        self._file_times = {}
        self._init_file_times()

    def _init_file_times(self):
        for watch_dir in self.watch_dirs:
            p = Path(watch_dir)
            if p.exists():
                for f in p.rglob("*"):
                    if f.is_file() and f.suffix in self.extensions:
                        self._file_times[str(f)] = f.stat().st_mtime

    def start(self):
        self._running = True

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _watch_loop(self):
        pass


class HotReloadPlugin:
    def __init__(self):
        self.plugin_loader_instance = None
        self.watcher: Optional[FileWatcher] = None
        self.watch_dirs: list[str] = []
        self.watch_extensions: list[str] = [".py", ".json"]

    def init(self, deps: dict = None):
        if not self.watch_dirs:
            self.watch_dirs = ["store"]
        self.start_watching()

    def stop(self):
        if self.watcher:
            self.watcher.stop()

    def set_plugin_loader(self, plugin_loader):
        self.plugin_loader_instance = plugin_loader

    def set_watch_dirs(self, dirs: list[str]):
        self.watch_dirs = dirs

    def start_watching(self):
        if self.watch_dirs and self.plugin_loader_instance:
            self.watcher = FileWatcher(
                self.watch_dirs,
                self.watch_extensions,
                self._on_file_change
            )
            self.watcher.start()

    def _on_file_change(self, changes: list[tuple[str, Path]]):
        for change_type, file_path in changes:
            pass

    def load_plugin(self, plugin_dir: Path) -> bool:
        try:
            plugin_name = plugin_dir.name
            if plugin_name in self.plugin_loader_instance.plugins:
                raise HotReloadError(f"Plugin already exists: {plugin_name}")

            self.plugin_loader_instance.load(plugin_dir)
            info = self.plugin_loader_instance.plugins[plugin_name]
            instance = info["instance"]
            instance.init()
            instance.start()
            return True
        except Exception as e:
            raise HotReloadError(f"Failed to load plugin: {e}")

    def unload_plugin(self, plugin_name: str) -> bool:
        try:
            self.plugin_loader_instance.unload(plugin_name)
            return True
        except Exception as e:
            raise HotReloadError(f"Failed to unload plugin: {e}")

    def reload_plugin(self, plugin_name: str, plugin_dir: Path) -> bool:
        try:
            self.unload_plugin(plugin_name)
            return self.load_plugin(plugin_dir)
        except Exception as e:
            raise HotReloadError(f"Failed to reload plugin: {e}")


def register_plugin_type(name, cls):
    pass


def New():
    return HotReloadPlugin()
