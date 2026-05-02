
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60, half_open_requests: int = 1):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_requests:
                self.state = CircuitState.CLOSED
                self.half_open_calls = 0

    def _on_failure(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0

    def get_state(self) -> str:
        return self.state
