    __slots__ = ('method', 'path', 'handler', '_pattern_parts')
    
    def __init__(self, method: str, path: str, handler: Callable):
        self.method = method
        self.path = path
        self.handler = handler
        self._pattern_parts = path.strip("/").split("/") if ":" in path else None


@lru_cache(maxsize=1024)
def match_path(pattern: str, path: str) -> bool:
    if pattern == path:
        return True
    
    pattern_parts = _get_pattern_parts(pattern)
    if pattern_parts is None:
        return False
    
    path_parts = path.strip("/").split("/")
    
    last_pattern = pattern_parts[-1]
    is_wildcard = _is_wildcard_param(last_pattern)
    
    if is_wildcard and len(path_parts) >= len(pattern_parts):
        for i, p in enumerate(pattern_parts[:-1]):
            if i >= len(path_parts):
                return False
            if not p.startswith(":") and p != path_parts[i]:
                return False
        return True
    
    if len(pattern_parts) != len(path_parts):
        return False
    
    for p, a in zip(pattern_parts, path_parts):
        if not p.startswith(":") and p != a:
            return False
    
    return True


def _is_wildcard_param(param: str) -> bool:
    if ":" not in pattern:
        return None
    return pattern.strip("/").split("/")


@lru_cache(maxsize=1024)
def extract_path_params(pattern: str, path: str) -> dict[str, str]:
    params = {}
    
    pattern_parts = _get_pattern_parts(pattern)
    if pattern_parts is None:
        return params
    
    path_parts = path.strip("/").split("/")
    
    last_pattern = pattern_parts[-1]
    is_wildcard = _is_wildcard_param(last_pattern)
    use_wildcard = is_wildcard and len(path_parts) > len(pattern_parts)
    
    if use_wildcard:
        parts_to_process = pattern_parts[:-1]
    else:
        parts_to_process = pattern_parts
    
    for i, p in enumerate(parts_to_process):
        if i < len(path_parts) and p.startswith(":"):
            param_name = p[1:]            params[param_name] = path_parts[i]
    
    if use_wildcard:
        param_name = last_pattern[1:]
        remaining = "/".join(path_parts[len(pattern_parts) - 1:])
        params[param_name] = remaining
    
    return params


class BaseRouter:
    
    def __init__(self):
        self.routes: list[BaseRoute] = []
    
    def add(self, method: str, path: str, handler: Callable):
        self.add("GET", path, handler)
    
    def post(self, path: str, handler: Callable):
        self.add("PUT", path, handler)
    
    def delete(self, path: str, handler: Callable):
        
        Args:
            method: HTTP 方法
            path: 请求路径
        
        Returns:
            (路由，路径参数) 或 None
        for route in self.routes:
            if route.method == method and match_path(route.path, path):
                params = extract_path_params(route.path, path)
                return route, params
        return None
