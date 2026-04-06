"""WebSocket 中间件链"""
from typing import Callable, Optional, Any


class WsMiddleware:
    """WebSocket 中间件基类"""
    async def process(self, client: Any, message: str, next_fn: Callable) -> Optional[str]:
        """处理消息"""
        return await next_fn()


class AuthMiddleware(WsMiddleware):
    """认证中间件"""
    async def process(self, client, message, next_fn):
        # 可以在这里验证 token
        return await next_fn()


class WsMiddlewareChain:
    """WebSocket 中间件链"""

    def __init__(self):
        self.middlewares: list[WsMiddleware] = []

    def add(self, middleware: WsMiddleware):
        """添加中间件"""
        self.middlewares.append(middleware)

    async def run(self, client, message) -> Optional[str]:
        """执行中间件链"""
        idx = 0

        async def next_fn():
            nonlocal idx
            if idx < len(self.middlewares):
                mw = self.middlewares[idx]
                idx += 1
                return await mw.process(client, message, next_fn)
            return message

        return await next_fn()
