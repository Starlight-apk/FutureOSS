    type: str
    source_plugin: str
    payload: Any = None
    context: dict[str, Any] = field(default_factory=dict)


class EventBus:
        self._history.append(event)
        handlers = self._handlers.get(event.type, [])
        wildcard_handlers = self._handlers.get("*", [])
        for handler in handlers + wildcard_handlers:
            try:
                handler(event)
            except Exception as e:
                import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
                pass

    def on(self, event_type: str, handler: Callable):
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass

    def once(self, event_type: str, handler: Callable):
        if event_type:
            return [e for e in self._history if e.type == event_type]
        return self._history.copy()

    def clear_history(self):

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._channels: dict[str, list[str]] = {}

    def create_channel(self, name: str, plugins: list[str]):
        if channel not in self._channels:
            return
        event = BridgeEvent(
            type=f"broadcast.{channel}",
            source_plugin=source_plugin,
            payload=payload
        )
        self.event_bus.emit(event)

    def get_channels(self) -> dict[str, list[str]]:

    def __init__(self):
        self._services: dict[str, dict[str, Callable]] = {}

    def register(self, plugin_name: str, service_name: str, handler: Callable):
        if plugin_name in self._services:
            if service_name:
                self._services[plugin_name].pop(service_name, None)
            else:
                del self._services[plugin_name]

    def call(self, plugin_name: str, service_name: str, *args, **kwargs) -> Any:
        if plugin_name:
            return self._services.get(plugin_name, {}).copy()
        return {k: v.copy() for k, v in self._services.items()}


class BridgeManager:
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
        return self._bridges.copy()


class PluginBridgePlugin(Plugin):
        self.broadcast = BroadcastManager(self.event_bus)
        self.bridge = BridgeManager(self.event_bus)

    def start(self):
        self.event_bus.clear_history()

    def set_plugin_storage(self, storage_plugin):
