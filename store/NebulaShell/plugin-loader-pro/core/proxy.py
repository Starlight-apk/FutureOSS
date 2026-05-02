    pass


class PluginProxy:
        if name not in self._allowed_plugins and "*" not in self._allowed_plugins:
            raise PermissionError(
                f"插件 '{self._plugin_name}' 无权访问插件 '{name}'"
            )
        if name not in self._all_plugins:
            return None
        return self._all_plugins[name]["instance"]

    def list_plugins(self) -> list[str]:
