    pass


class TimeoutController:
        def handler(signum, frame):
            raise TimeoutError(f"执行超时 (>{self.timeout}s)")

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.timeout)

        try:
            result = func(*args, **kwargs)
            signal.alarm(0)
            return result
        finally:
            signal.signal(signal.SIGALRM, old_handler)
