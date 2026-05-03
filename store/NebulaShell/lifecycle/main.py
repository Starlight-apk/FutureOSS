class LifecycleState:
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"


class LifecycleError(Exception):
    pass


class Lifecycle:
    VALID_TRANSITIONS = {
        LifecycleState.PENDING: [LifecycleState.RUNNING],
        LifecycleState.RUNNING: [LifecycleState.STOPPED],
        LifecycleState.STOPPED: [LifecycleState.RUNNING],
    }

    def __init__(self, name: str):
        self.name = name
        self.state = LifecycleState.PENDING
        self._hooks: dict[str, list[Callable]] = {
            "before_start": [],
            "after_start": [],
            "before_stop": [],
            "after_stop": [],
        }
        self._extensions: dict[str, Any] = {}

    def add_extension(self, name: str, extension: Any):
        self._extensions[name] = extension

    def get_extension(self, name: str) -> Any:
        return self._extensions.get(name)

    def start(self):
        for hook in self._hooks["before_start"]:
            hook(self)
        self.transition(LifecycleState.RUNNING)
        for hook in self._hooks["after_start"]:
            hook(self)

    def stop(self):
        if self.state == LifecycleState.RUNNING:
            for hook in self._hooks["before_stop"]:
                hook(self)
            self.transition(LifecycleState.STOPPED)
            for hook in self._hooks["after_stop"]:
                hook(self)

    def restart(self):
        self.stop()
        self.start()

    def on(self, event: str, hook: Callable):
        if event in self._hooks:
            self._hooks[event].append(hook)

    def transition(self, target_state: LifecycleState):
        valid = self.VALID_TRANSITIONS.get(self.state, [])
        if target_state in valid:
            self.state = target_state
        else:
            raise LifecycleError(f"Cannot transition from {self.state} to {target_state}")


class LifecycleManager:
    def __init__(self):
        self.lifecycles: dict[str, Lifecycle] = {}

    def init(self, deps: dict = None):
        pass

    def create(self, name: str) -> Lifecycle:
        lifecycle = Lifecycle(name)
        self.lifecycles[name] = lifecycle
        return lifecycle

    def get(self, name: str) -> Optional[Lifecycle]:
        return self.lifecycles.get(name)

    def start_all(self):
        for lc in self.lifecycles.values():
            try:
                lc.start()
            except LifecycleError:
                pass

    def stop_all(self):
        for lc in self.lifecycles.values():
            try:
                lc.stop()
            except LifecycleError:
                pass
