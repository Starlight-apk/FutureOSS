from dataclasses import dataclass, field
from typing import Any, Callable
from pathlib import Path
import importlib.util

from oss.plugin.types import Plugin


@dataclass
class BridgeEvent:
    type: str
    source_plugin: str
    payload: Any = None
    context: dict[str, Any] = field(default_factory=dict)


class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
        self._history: list[BridgeEvent] = []

    def emit(self, event: BridgeEvent):
        self._history.append(event)
        handlers = self._handlers.get(event.type, [])
        wildcard_handlers = self._handlers.get("*", [])
        for handler in handlers + wildcard_handlers:
            try:
                handler(event)
            except Exception as e:
                import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()

    def on(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable):
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass

    def once(self, event_type: str, handler: Callable):
        def wrapper(event):
            self.off(event_type, wrapper)
            handler(event)
        self.on(event_type, wrapper)

    def get_history(self, event_type: str = None) -> list[BridgeEvent]:
        if event_type:
            return [e for e in self._history if e.type == event_type]
        return self._history.copy()

    def clear_history(self):
        self._history.clear()


class BroadcastManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._channels: dict[str, list[str]] = {}

    def create_channel(self, name: str, plugins: list[str]):
        self._channels[name] = plugins

    def broadcast(self, channel: str, payload: Any, source_plugin: str = ""):
        if channel not in self._channels:
            return
        event = BridgeEvent(
            type=f"broadcast.{channel}",
            source_plugin=source_plugin,
            payload=payload
        )
        self.event_bus.emit(event)

    def get_channels(self) -> dict[str, list[str]]:
        return dict(self._channels)


class ServiceRegistry:
    def __init__(self):
        self._services: dict[str, dict[str, Callable]] = {}

    def register(self, plugin_name: str, service_name: str, handler: Callable):
        if plugin_name not in self._services:
            self._services[plugin_name] = {}
        self._services[plugin_name][service_name] = handler

    def unregister(self, plugin_name: str, service_name: str = None):
        if plugin_name in self._services:
            if service_name:
                self._services[plugin_name].pop(service_name, None)
            else:
                del self._services[plugin_name]

    def call(self, plugin_name: str, service_name: str, *args, **kwargs) -> Any:
        plugin = self._services.get(plugin_name)
        if plugin and service_name in plugin:
            return plugin[service_name](*args, **kwargs)
        return None

    def list_services(self, plugin_name: str = None) -> dict:
        if plugin_name:
            return self._services.get(plugin_name, {}).copy()
        return {k: v.copy() for k, v in self._services.items()}


class BridgeManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._bridges: dict = {}

    def create_bridge(self, name: str, from_plugin: str, to_plugin: str, event_mapping: dict):
        self._bridges[name] = {
            "from": from_plugin,
            "to": to_plugin,
            "mapping": event_mapping,
        }
        for src_event, dst_event in event_mapping.items():
            def handler(event, dst_event=dst_event):
                bridged = BridgeEvent(
                    type=dst_event,
                    source_plugin=event.source_plugin,
                    payload=event.payload,
                    context={**event.context, "_bridged_from": event.type}
                )
                self.event_bus.emit(bridged)
            self.event_bus.on(src_event, handler)

    def remove_bridge(self, name: str):
        self._bridges.pop(name, None)

    def get_bridges(self) -> dict:
        return self._bridges.copy()


_use_cache: dict[str, Any] = {}

def use(plugin_name: str):
    if plugin_name in _use_cache:
        return _use_cache[plugin_name]

    from oss.plugin.manager import get_plugin_manager
    manager = get_plugin_manager()
    if manager and plugin_name in manager.plugins:
        _use_cache[plugin_name] = manager.plugins[plugin_name]
        return _use_cache[plugin_name]

    from oss.config import get_config
    config = get_config()
    store_dir = Path(config.get("store_dir", "store"))

    if not store_dir.exists():
        return None

    for ns_dir in store_dir.iterdir():
        if not ns_dir.is_dir():
            continue
        for pdir in ns_dir.iterdir():
            if not pdir.is_dir():
                continue
            manifest = pdir / "manifest.json"
            if not manifest.exists():
                continue
            try:
                meta = json.loads(manifest.read_text())
                name = meta.get("name", pdir.name)
                if name == plugin_name:
                    main_file = pdir / "main.py"
                    if not main_file.exists():
                        continue
                    PluginClass = None
                    if manager and plugin_name in manager._plugin_types:
                        PluginClass = manager._plugin_types[plugin_name]
                    if PluginClass is None:
                        spec = importlib.util.spec_from_file_location(f"use_{plugin_name}", str(main_file))
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(mod)
                            for attr in dir(mod):
                                cls = getattr(mod, attr)
                                if isinstance(cls, type) and issubclass(cls, Plugin) and cls is not Plugin:
                                    PluginClass = cls
                                    break
                    if PluginClass:
                        instance = PluginClass() if isinstance(PluginClass, type) else PluginClass
                        _use_cache[plugin_name] = instance
                        if manager:
                            manager.plugins[plugin_name] = instance
                        if hasattr(instance, "start"):
                            instance.start()
                        return instance
            except (json.JSONDecodeError, OSError):
                continue
    return None


class PluginBridgePlugin(Plugin):
    def __init__(self):
        self.event_bus = EventBus()
        self.services = ServiceRegistry()
        self.broadcast = BroadcastManager(self.event_bus)
        self.bridge = BridgeManager(self.event_bus)

    def start(self):
        self.event_bus.clear_history()

    def set_plugin_storage(self, storage_plugin):
        pass

    def stop(self):
        self.event_bus.clear_history()
