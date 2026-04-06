"""Web 路由器"""
from typing import Callable, Optional, Any


class WebRoute:
    """Web 路由"""
    def __init__(self, method: str, path: str, handler: Callable):
        self.method = method
        self.path = path
        self.handler = handler


class WebRouter:
    """Web 路由器"""

    def __init__(self):
        self.routes: list[WebRoute] = []

    def add_route(self, method: str, path: str, handler: Callable):
        """添加路由"""
        self.routes.append(WebRoute(method, path, handler))

    def get(self, path: str, handler: Callable):
        """GET 路由"""
        self.add_route("GET", path, handler)

    def post(self, path: str, handler: Callable):
        """POST 路由"""
        self.add_route("POST", path, handler)

    def put(self, path: str, handler: Callable):
        """PUT 路由"""
        self.add_route("PUT", path, handler)

    def delete(self, path: str, handler: Callable):
        """DELETE 路由"""
        self.add_route("DELETE", path, handler)

    def handle(self, request: dict) -> Optional[Any]:
        """处理请求"""
        method = request.get("method", "GET")
        path = request.get("path", "/")

        for route in self.routes:
            if route.method == method and self._match(route.path, path):
                return route.handler(request)

        return None

    def _match(self, pattern: str, path: str) -> bool:
        """路径匹配"""
        if pattern == path:
            return True
        if ":" in pattern:
            pattern_parts = pattern.strip("/").split("/")
            path_parts = path.strip("/").split("/")
            if len(pattern_parts) != len(path_parts):
                return False
            for p, a in zip(pattern_parts, path_parts):
                if not p.startswith(":") and p != a:
                    return False
            return True
        return False
