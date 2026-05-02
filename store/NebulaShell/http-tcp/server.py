
    def __init__(self, conn: socket.socket, address: tuple):
        self.conn = conn
        self.address = address
        self.id = f"{address[0]}:{address[1]}"

    def send(self, data: bytes):
        self.conn.close()


class TcpHttpServer:
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.host, self.port))
        self._server.listen(128)
        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        print(f"[http-tcp] 服务器启动: {self.host}:{self.port}")

    def _accept_loop(self):
        buffer = b""
        try:
            while self._running:
                data = client.conn.recv(4096)
                if not data:
                    break
                buffer += data

                if b"\r\n\r\n" in buffer:
                    header_end = buffer.find(b"\r\n\r\n")
                    header_text = buffer[:header_end].decode("utf-8", errors="replace")
                    
                    content_length = 0
                    for line in header_text.split("\r\n")[1:]:
                        if line.lower().startswith("content-length:"):
                            content_length = int(line.split(":", 1)[1].strip())
                            break
                    
                    body_start_pos = header_end + 4                    body_received = len(buffer) - body_start_pos
                    
                    if body_received < content_length:
                        while body_received < content_length:
                            remaining = content_length - body_received
                            chunk = client.conn.recv(min(4096, remaining))
                            if not chunk:
                                break
                            buffer += chunk
                            body_received += len(chunk)
                    
                    request = self._parse_request(buffer)
                    if request:
                        if self.event_bus:
                            self.event_bus.emit(TcpEvent(
                                type=EVENT_REQUEST,
                                client=client,
                                context={"request": request}
                            ))

                        response = self.router.handle(request)

                        response_bytes = self._format_response(response)
                        client.send(response_bytes)

                        if self.event_bus:
                            self.event_bus.emit(TcpEvent(
                                type=EVENT_RESPONSE,
                                client=client,
                                data=response_bytes
                            ))

                        buffer = b""

        except ConnectionResetError:
            pass
        except BrokenPipeError:
            pass
        except OSError as e:
            if self.event_bus:
                self.event_bus.emit(TcpEvent(type=EVENT_ERROR, client=client, context={"error": f"OSError: {e}"}))
        except Exception as e:
            if self.event_bus:
                self.event_bus.emit(TcpEvent(type=EVENT_ERROR, client=client, context={"error": f"{type(e).__name__}: {e}"}))
        finally:
            del self._clients[client.id]
            client.close()
            if self.event_bus:
                self.event_bus.emit(TcpEvent(type=EVENT_DISCONNECT, client=client))

    def _parse_request(self, data: bytes) -> Optional[dict]:
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
        return list(self._clients.values())
