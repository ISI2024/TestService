from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections = dict()

    async def connect(self, websocket: WebSocket, login: str):
        await websocket.accept()
        self.active_connections[login] = websocket

    async def disconnect(self, login: str):
        if login in self.active_connections[login]:
            self.active_connections[login] = None

    async def send_personal_message(self, message: str, login: str):
        await self.active_connections[login].send_text(message)
