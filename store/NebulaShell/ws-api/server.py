
    def __init__(self, websocket, path: str):
        self.websocket = websocket
        self.path = path
        self.id = id(websocket)
        self.closed = False

    async def send(self, message: Any):
        self.closed = True
        await self.websocket.close()


class WsServer:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        if path is None:
            try:
                path = websocket.request.path
            except AttributeError:
                path = "/"
        
        client = WsClient(websocket, path)
        self._clients[client.id] = client

        self.event_bus.emit(WsEvent(
            type=EVENT_CONNECT,
            client=client,
            path=path
        ))

        try:
            async for message in websocket:
                self.event_bus.emit(WsEvent(
                    type=EVENT_MESSAGE,
                    client=client,
                    path=path,
                    message=message
                ))

                await self.router.handle(client, path, message)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            del self._clients[client.id]
            self.event_bus.emit(WsEvent(
                type=EVENT_DISCONNECT,
                client=client,
                path=path
            ))

    def stop(self):
        async def _broadcast():
            for client_id, client in self._clients.items():
                if exclude_client and client_id == exclude_client:
                    continue
                await client.send(message)
        
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(_broadcast(), self._loop)

    def get_clients(self) -> list[WsClient]:
