
    def __init__(self, config: ProConfig):
        self.config = config
        self.plugins: dict[str, dict[str, Any]] = {}
        self.capability_registry = CapabilityRegistry()
        self._breakers: dict[str, CircuitBreaker] = {}
        self._health_checker = HealthChecker(
            config.health_check.interval,
            config.health_check.timeout,
            config.health_check.max_failures
        )
        self._auto_recovery = AutoRecovery(
            config.auto_recovery.max_attempts,
            config.auto_recovery.delay
        )

    def load_all(self, store_dir: str = "store"):
        if not store_dir.exists():
            return

        for author_dir in store_dir.iterdir():
            if not author_dir.is_dir():
                continue

            for plugin_dir in author_dir.iterdir():
                if not plugin_dir.is_dir():
                    continue

                main_file = plugin_dir / "main.py"
                if not main_file.exists():
                    continue

                self._load_single_plugin(plugin_dir)

    def _load_single_plugin(self, plugin_dir: Path) -> Optional[Any]:
        ProLogger.info("manager", "开始初始化所有插件...")

        self._inject_dependencies()
        ordered = self._get_ordered_plugins()

        for name in ordered:
            self._safe_init(name)

        ProLogger.info("manager", "开始启动所有插件...")
        for name in ordered:
            self._safe_start(name)

        self._health_checker.start(
            on_failure_callback=self._on_plugin_failure
        )

    def _safe_init(self, name: str):
        info = self.plugins[name]
        instance = info["instance"]
        breaker = self._breakers[name]

        try:
            breaker.call(instance.start)
            info["info"].status = "running"
            self._health_checker.add_plugin(name, instance)
            ProLogger.info("manager", f"已启动: {name}")
        except Exception as e:
            ProLogger.error("manager", f"启动失败 {name}: {type(e).__name__}: {e}")
            info["info"].status = "error"
            info["info"].error_count += 1
            info["info"].last_error = str(e)

    def stop_all(self):
        info = self.plugins[name]
        instance = info["instance"]

        try:
            instance.stop()
            info["info"].status = "stopped"
            ProLogger.info("manager", f"已停止: {name}")
        except Exception as e:
            ProLogger.warn("manager", f"停止异常 {name}: {type(e).__name__}: {e}")

    def _on_plugin_failure(self, name: str):
        name_map = {}
        for name in self.plugins:
            clean = name.rstrip("}")
            name_map[clean] = name
            name_map[clean + "}"] = name

        for name, info in self.plugins.items():
            deps = info["info"].dependencies
            if not deps:
                continue

            for dep_name in deps:
                actual_dep = name_map.get(dep_name) or name_map.get(dep_name + "}")
                if actual_dep and actual_dep in self.plugins:
                    dep_instance = self.plugins[actual_dep]["instance"]
                    setter = f"set_{dep_name.replace('-', '_')}"

                    if hasattr(info["instance"], setter):
                        try:
                            getattr(info["instance"], setter)(dep_instance)
                            ProLogger.info("inject", f"{name} <- {actual_dep}")
                        except Exception as e:
                            ProLogger.error("inject", f"注入失败 {name}.{setter}: {type(e).__name__}: {e}")

    def _get_ordered_plugins(self) -> list[str]:
