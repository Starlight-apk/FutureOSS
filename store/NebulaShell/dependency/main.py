    pass


class DependencyResolver:
        self.graph[name] = dependencies

    def resolve(self) -> list[str]:
        self._detect_cycles()

        in_degree: dict[str, int] = {name: 0 for name in self.graph}
        who_depends_on: dict[str, list[str]] = {name: [] for name in self.graph}
        
        for name, deps in self.graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[name] += 1                    who_depends_on[dep].append(name)
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for dependent in who_depends_on.get(node, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self.graph):
            raise DependencyError("无法解析依赖，可能存在循环依赖")

        return result

    def _detect_cycles(self):
        all_deps = set()
        for deps in self.graph.values():
            all_deps.update(deps)
        all_plugins = set(self.graph.keys())
        return list(all_deps - all_plugins)


class DependencyPlugin(Plugin):
        pass

    def start(self):
        pass

    def add_plugin(self, name: str, dependencies: list[str]):
        return self.resolver.resolve()

    def get_missing_deps(self) -> list[str]:
        return self.resolve()


register_plugin_type("DependencyResolver", DependencyResolver)
register_plugin_type("DependencyError", DependencyError)


def New():
    return DependencyPlugin()
