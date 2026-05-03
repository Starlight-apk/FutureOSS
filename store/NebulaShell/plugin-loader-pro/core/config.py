class ProConfig:
    def __init__(self, config: dict = None):
        config = config or {}
        self.failure_threshold = config.get("failure_threshold", 3)
        self.recovery_timeout = config.get("recovery_timeout", 60)
        self.half_open_requests = config.get("half_open_requests", 1)


class RetryConfig:
    def __init__(self, config: dict = None):
        config = config or {}
        self.interval = config.get("interval", 30)
        self.timeout = config.get("timeout", 5)
        self.max_failures = config.get("max_failures", 5)


class AutoRecoveryConfig:
    def __init__(self, config: dict = None):
        config = config or {}
        self.enabled = config.get("enabled", True)
        self.timeout_per_plugin = config.get("timeout_per_plugin", 30)


