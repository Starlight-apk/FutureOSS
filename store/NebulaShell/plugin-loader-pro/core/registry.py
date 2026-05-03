
class ProCapabilityRegistry:
    def __init__(self, permission_check: bool = True):
        self.providers: dict[str, dict[str, Any]] = {}
        self.consumers: dict[str, list[str]] = {}
        self.permission_check = permission_check

    def register_provider(self, capability: str, plugin_name: str, instance: Any):
        if capability not in self.consumers:
            self.consumers[capability] = []
        if plugin_name not in self.consumers[capability]:
            self.consumers[capability].append(plugin_name)

    def get_provider(self, capability: str, requester: str = "",
                     allowed_plugins: list[str] = None) -> Optional[Any]:
        return None
