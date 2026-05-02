
    def __init__(self, interval: int = 30, timeout: int = 5, max_failures: int = 5):
        self.interval = interval
        self.timeout = timeout
        self.max_failures = max_failures

        self._running = False
        self._thread = None
        self._plugins: dict[str, Any] = {}
        self._failure_counts: dict[str, int] = {}
        self._on_failure_callback = None

    def add_plugin(self, name: str, instance: Any):
        self._on_failure_callback = on_failure_callback
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
        ProLogger.info("health", "健康检查已启动")

    def stop(self):
        while self._running:
            for name, instance in self._plugins.items():
                self._check_plugin(name, instance)
            time.sleep(self.interval)

    def _check_plugin(self, name: str, instance: Any):
        self._failure_counts[name] = self._failure_counts.get(name, 0) + 1

        if self._failure_counts[name] >= self.max_failures:
            ProLogger.warn("health", f"插件 {name} 连续失败 {self._failure_counts[name]} 次")
            if self._on_failure_callback:
                self._on_failure_callback(name)

    def reset_failure_count(self, name: str):
        return self._failure_counts.get(name, 0)
