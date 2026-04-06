"""TCP HTTP 服务器核心"""
import socket
import threading
import re
from typing import Any, Callable, Optional
from .events import TcpEvent, EVENT_CONNECT, EVENT_DISCONNECT, EVENT_DATA, EVENT_REQUEST, EVENT_RESPONSE


class TcpClient:
    """TCP 客户端连接"""

    def __init__(self, conn: socket.socket, address: tuple):
        self.conn = conn
        self.address = address
        self.id = f"{address[0]}:{address[1]}"

    def send(self, data: bytes):
        """发送数据"""
        self.conn.sendall(data)

    def close(self):
        """关闭连接"""
        self.conn.close()


class TcpHttpServer:
    """TCP HTTP 服务器"""

    def __init__(self, router, middleware, event_bus=None, host="0.0.0.0", port=8082):
        self.host = host
        self.port = port
        self.router = router
        self.middleware = middleware
        self.event_bus = event_bus
        self._server = None
        self._thread = None
        self._running = False
        self._clients: dict[str, TcpClient] = {}

    def start(self):
        """启动服务器"""
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.host, self.port))
        self._server.listen(128)
        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        print(f"[http-tcp] 服务器启动: {self.host}:{self.port}")

    def _accept_loop(self):
        """接受连接循环"""
        while self._running:
            try:
                conn, address = self._server.accept()
                client = TcpClient(conn, address)
                self._clients[client.id] = client

                # 触发连接事件
                if self.event_bus:
                    self.event_bus.emit(TcpEvent(type=EVENT_CONNECT, client=client))

                # 启动处理线程
                t = threading.Thread(target=self._handle_client, args=(client,), daemon=True)
                t.start()
            except Exception as e:
                if self._running:
                    print(f"[http-tcp] 接受连接失败: {e}")

    def _handle_client(self, client: TcpClient):
        """处理客户端请求"""
        buffer = b""
        try:
            while self._running:
                data = client.conn.recv(4096)
                if not data:
                    break
                buffer += data

                # 检查 HTTP 请求是否完整
                if b"\r\n\r\n" in buffer:
                    request = self._parse_request(buffer)
                    if request:
                        # 触发请求事件
                        if self.event_bus:
                            self.event_bus.emit(TcpEvent(
                                type=EVENT_REQUEST,
                                client=client,
                                context={"request": request}
                            ))

                        # 路由处理
                        response = self.router.handle(request)

                        # 发送响应
                        response_bytes = self._format_response(response)
                        client.send(response_bytes)

                        # 触发响应事件
                        if self.event_bus:
                            self.event_bus.emit(TcpEvent(
                                type=EVENT_RESPONSE,
                                client=client,
                                data=response_bytes
                            ))

                        buffer = b""

        except Exception as e:
            if self.event_bus:
                self.event_bus.emit(TcpEvent(type=EVENT_ERROR, client=client, context={"error": str(e)}))
        finally:
            del self._clients[client.id]
            client.close()
            if self.event_bus:
                self.event_bus.emit(TcpEvent(type=EVENT_DISCONNECT, client=client))

    def _parse_request(self, data: bytes) -> Optional[dict]:
        """解析 HTTP 请求"""
        try:
            text = data.decode("utf-8", errors="replace")
            lines = text.split("\r\n")
            if not lines:
                return None

            # 解析请求行
            match = re.match(r'(\w+)\s+(\S+)\s+HTTP/(\d\.\d)', lines[0])
            if not match:
                return None

            method, path, version = match.groups()

            # 解析头
            headers = {}
            body_start = 0
            for i, line in enumerate(lines[1:], 1):
                if line == "":
                    body_start = i + 1
                    break
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()

            # 解析体
            content_length = int(headers.get("Content-Length", 0))
            body = "\r\n".join(lines[body_start:]) if body_start else ""

            return {
                "method": method,
                "path": path,
                "version": version,
                "headers": headers,
                "body": body,
            }
        except Exception:
            return None

    def _format_response(self, response: dict) -> bytes:
        """格式化 HTTP 响应"""
        status = response.get("status", 200)
        headers = response.get("headers", {})
        body = response.get("body", "")

        status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}.get(status, "OK")

        response_lines = [
            f"HTTP/1.1 {status} {status_text}",
        ]

        if "Content-Type" not in headers:
            headers["Content-Type"] = "text/plain; charset=utf-8"
        headers["Content-Length"] = str(len(body))

        for key, value in headers.items():
            response_lines.append(f"{key}: {value}")

        response_lines.append("")
        response_lines.append(body)

        return "\r\n".join(response_lines).encode("utf-8")

    def stop(self):
        """停止服务器"""
        self._running = False
        for client in self._clients.values():
            client.close()
        if self._server:
            self._server.close()
        print("[http-tcp] 服务器已停止")

    def get_clients(self) -> list[TcpClient]:
        """获取所有客户端"""
        return list(self._clients.values())
