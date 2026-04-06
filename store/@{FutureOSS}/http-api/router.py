"""路由器 - 路径匹配和处理器分发"""
from typing import Callable, Optional
from .server import Request, Response


class Route:
    """路由定义"""
    def __init__(self, method: str, path: str, handler: Callable):
        self.method = method
        self.path = path
        self.handler = handler


class Router:
    """路由器"""

    def __init__(self):
        self.routes: list[Route] = []

    def add(self, method: str, path: str, handler: Callable):
        """添加路由"""
        self.routes.append(Route(method, path, handler))

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

    def handle(self, request: Request) -> Response:
        """处理请求"""
        for route in self.routes:
            if route.method == request.method and self._match(route.path, request.path):
                return route.handler(request)
        return Response(status=404, body='{"error": "Not Found"}')

    def _match(self, pattern: str, path: str) -> bool:
        """路径匹配"""
        if pattern == path:
            return True
        if ":" in pattern:
            pattern_parts = pattern.strip("/").split("/")
            path_parts = path.strip("/").split("/")
            
            # 检查前缀是否匹配
            for i, p in enumerate(pattern_parts):
                if i >= len(path_parts):
                    return False
                if not p.startswith(":") and p != path_parts[i]:
                    return False
            
            # 如果最后一个 pattern 是 :path（通配符），允许更多路径段
            last_pattern = pattern_parts[-1]
            if last_pattern.startswith(":") and len(path_parts) >= len(pattern_parts):
                return True
            
            # 否则必须精确匹配段数
            if len(pattern_parts) != len(path_parts):
                return False
            
            return True
        return False
