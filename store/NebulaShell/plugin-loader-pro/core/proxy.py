class ProPluginProxy:
    pass


class PluginProxy:
    def __init__(self, plugin_name: str, allowed_plugins: list[str], all_plugins: dict):
        self._plugin_name = plugin_name
        self._allowed_plugins = allowed_plugins
        self._all_plugins = all_plugins

    def get_plugin(self, name: str):
        if name not in self._allowed_plugins and "*" not in self._allowed_plugins:
            raise PermissionError(
                f"插件 '{self._plugin_name}' 无权访问插件 '{name}'"
            )
        if name not in self._all_plugins:
            return None
        return self._all_plugins[name]["instance"]

    def list_plugins(self) -> list[str]:
        return list(self._all_plugins.keys())
