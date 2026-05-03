
class RetryHandler:
    def __init__(self, config: RetryConfig = None):
        config = config or RetryConfig()
        self.max_retries = config.max_retries
        self.backoff_factor = config.backoff_factor
        self.initial_delay = config.initial_delay

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
