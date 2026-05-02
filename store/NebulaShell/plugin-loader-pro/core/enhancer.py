
    def __init__(self, plugin_manager, config: ProConfig):
        self.pm = plugin_manager
        self.config = config
        self._breakers = {}
        self._health_checker = None
        self._auto_recovery = AutoRecovery(
            config.auto_recovery.max_attempts,
            config.auto_recovery.delay
        )
        self._enhanced = False

    def enhance(self):
        for name, info in self.pm.plugins.items():
            self._breakers[name] = CircuitBreaker(
                self.config.circuit_breaker.failure_threshold,
                self.config.circuit_breaker.recovery_timeout,
                self.config.circuit_breaker.half_open_requests
            )
            ProLogger.debug("enhancer", f"为 {name} 创建熔断器")

    def _wrap_start_methods(self):
        ordered = self._get_ordered_plugins()

        for name in ordered:
            self._safe_call(name, 'init', '初始化')

        for name in ordered:
            self._safe_call(name, 'start', '启动')

    def _safe_start_all(self):
        info = self.pm.plugins.get(name)
        if not info:
            return

        instance = info.get("instance")
        if not instance or not hasattr(instance, method):
            return

        breaker = self._breakers.get(name)
        if not breaker:
            try:
                getattr(instance, method)()
            except Exception as e:
                ProLogger.error("safe", f"{name} {action}失败: {type(e).__name__}: {e}")
                self._on_plugin_error(name, info, str(e))
            return

        def do_call():
            return getattr(instance, method)()

        try:
            breaker.call(do_call)
            info["info"].error_count = 0
            ProLogger.info("safe", f"{name} {action}成功")
        except Exception as e:
            ProLogger.error("safe", f"{name} {action}失败: {type(e).__name__}: {e}")
            self._on_plugin_error(name, info, str(e))

    def _on_plugin_error(self, name: str, info: dict, error: str):
        self._health_checker = HealthChecker(
            self.config.health_check.interval,
            self.config.health_check.timeout,
            self.config.health_check.max_failures
        )

        for name, info in self.pm.plugins.items():
            self._health_checker.add_plugin(name, info["instance"])

        self._health_checker.start(
            on_failure_callback=self._on_health_check_failure
        )
        ProLogger.info("enhancer", "健康检查已启动")

    def _on_health_check_failure(self, name: str):
        ordered = []
        visited = set()

        def visit(name):
            if name in visited:
                return
            visited.add(name)

            info = self.pm.plugins.get(name)
            if not info:
                return

            for dep in info["info"].dependencies:
                clean_dep = dep.rstrip("}")
                if clean_dep in self.pm.plugins:
                    visit(clean_dep)

            ordered.append(name)

        for name in self.pm.plugins:
            visit(name)

        return ordered

    def disable(self):
