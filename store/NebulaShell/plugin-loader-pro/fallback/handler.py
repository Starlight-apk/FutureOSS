class FallbackHandler:
    RETURN_DEFAULT = "return_default"
    RETURN_CACHE = "return_cache"
    RETURN_NULL = "return_null"
    CALL_ALTERNATIVE = "call_alternative"

    def __init__(self):
        self._cache = {}

    def execute(self, plugin_name: str, func: Callable, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self._cache[plugin_name] = result
            return result
        except Exception as e:
            ProLogger.warn("fallback", f"插件 {plugin_name} 执行失败，触发降级: {type(e).__name__}: {e}")
            return self._apply_fallback(plugin_name)

    def _apply_fallback(self, plugin_name: str) -> Any:
        return None
