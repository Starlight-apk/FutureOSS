    pass


class FileWatcher:
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                for f in watch_dir.rglob("*"):
                    if f.is_file() and f.suffix in self.extensions:
                        self._file_times[str(f)] = f.stat().st_mtime

    def start(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _watch_loop(self):

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
        self.plugin_loader_instance = plugin_loader

    def set_watch_dirs(self, dirs: list[str]):
        if self.watch_dirs and self.plugin_loader_instance:
            self.watcher = FileWatcher(
                self.watch_dirs,
                self.watch_extensions,
                self._on_file_change
            )
            self.watcher.start()

    def _on_file_change(self, changes: list[tuple[str, Path]]):
        try:
            plugin_name = plugin_dir.name
            if plugin_name in self.plugin_loader_instance.plugins:
                raise HotReloadError(f"插件已存在: {plugin_name}")

            self.plugin_loader_instance.load(plugin_dir)
            info = self.plugin_loader_instance.plugins[plugin_name]
            instance = info["instance"]
            instance.init()
            instance.start()
            return True
        except Exception as e:
            raise HotReloadError(f"加载插件失败: {e}")

    def unload_plugin(self, plugin_name: str) -> bool:
        try:
            self.unload_plugin(plugin_name)
            return self.load_plugin(plugin_dir)
        except Exception as e:
            raise HotReloadError(f"更新插件失败: {e}")


register_plugin_type("HotReloadError", HotReloadError)
register_plugin_type("FileWatcher", FileWatcher)


def New():
    return HotReloadPlugin()
