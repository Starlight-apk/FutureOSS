    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"


class LifecycleError(Exception):

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
        return self._extensions.get(name)

    def transition(self, target_state: LifecycleState):
        for hook in self._hooks["before_start"]:
            hook(self)
        self.transition(LifecycleState.RUNNING)
        for hook in self._hooks["after_start"]:
            hook(self)

    def stop(self):
        if self.state == LifecycleState.RUNNING:
            self.stop()
        self.start()

    def on(self, event: str, hook: Callable):

    def __init__(self):
        self.lifecycles: dict[str, Lifecycle] = {}

    def init(self, deps: dict = None):
        pass

    def stop(self):
        lifecycle = Lifecycle(name)
        self.lifecycles[name] = lifecycle
        return lifecycle

    def get(self, name: str) -> Optional[Lifecycle]:
        for lc in self.lifecycles.values():
            try:
                lc.start()
            except LifecycleError:
                pass

    def stop_all(self):
