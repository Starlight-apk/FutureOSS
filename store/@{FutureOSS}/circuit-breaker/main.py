"""熔断插件 - 为插件提供熔断能力"""
from oss.plugin.types import Plugin, register_plugin_type


class CircuitBreakerProvider:
    """熔断能力提供者"""

    def __init__(self):
        self.breakers: dict[str, "CircuitBreaker"] = {}

    def create(self, name: str, threshold: int = 5) -> "CircuitBreaker":
        breaker = CircuitBreaker(name, threshold)
        self.breakers[name] = breaker
        return breaker

    def get(self, name: str):
        return self.breakers.get(name)


class CircuitBreaker:
    """熔断器"""

    def __init__(self, name: str, threshold: int = 5):
        self.name = name
        self.threshold = threshold
        self.failures = 0
        self.state = "closed"  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            raise Exception(f"熔断器 '{self.name}' 已打开")

        try:
            result = func(*args, **kwargs)
            self.failures = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "open"
            raise e


class CircuitBreakerPlugin(Plugin):
    """熔断插件"""

    def __init__(self):
        self.provider = CircuitBreakerProvider()

    def init(self, deps: dict = None):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def get_provider(self):
        return self.provider


# 注册类型
register_plugin_type("CircuitBreakerProvider", CircuitBreakerProvider)
register_plugin_type("CircuitBreaker", CircuitBreaker)


def New():
    return CircuitBreakerPlugin()
