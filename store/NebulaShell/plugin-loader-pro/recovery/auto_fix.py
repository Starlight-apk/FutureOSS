
    def __init__(self, max_attempts: int = 3, delay: int = 10):
        self.max_attempts = max_attempts
        self.delay = delay
        self._recovery_attempts: dict[str, int] = {}

    def attempt_recovery(self, name: str, plugin_dir: Path,
                         module: any, instance: any) -> bool:
        self._recovery_attempts[name] = 0

    def get_attempts(self, name: str) -> int:
