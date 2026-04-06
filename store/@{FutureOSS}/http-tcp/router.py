"""TCP HTTP 路由器"""
from typing import Callable, Optional, Any


class TcpRoute:
    """TCP HTTP 路由"""
    def __init__(self, method: str, path: str, handler: Callable):
        self.method = method
        self.path = path
        self.handler = handler


class TcpRouter:
    """TCP HTTP 路由器"""

    def __init__(self):
        self.routes: list[TcpRoute] = []

    def add(self, method: str, path: str, handler: Callable):
        """添加路由"""
        self.routes.append(TcpRoute(method, path, handler))

    def get(self, path: str, handler: Callable):
        """GET 路由"""
        self.add("GET", path, handler)

    def post(self, path: str, handler: Callable):
        """POST 路由"""
        self.add("POST", path, handler)

    def put(self, path: str, handler: Callable):
        """PUT 路由"""
        self.add("PUT", path, handler)

    def delete(self, path: str, handler: Callable):
        """DELETE 路由"""
        self.add("DELETE", path, handler)

    def handle(self, request: dict) -> dict:
        """处理请求"""
        method = request.get("method", "GET")
        path = request.get("path", "/")

        for route in self.routes:
            if route.method == method and self._match(route.path, path):
                return route.handler(request)

        return {"status": 404, "headers": {}, "body": "Not Found"}

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
