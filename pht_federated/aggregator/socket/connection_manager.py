from typing import List, Dict

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class TrainConnectionManager:
    def __init__(self):
        self.active_train_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, train_id: str):
        logger.info(f"New Socket connection for train <{train_id}>: {websocket.client}")
        await websocket.accept()
        if isinstance(self.active_train_connections.get(train_id), list):
            self.active_train_connections[train_id].append(websocket)
        else:
            self.active_train_connections[train_id] = [websocket]

    async def disconnect(self, websocket: WebSocket, train_id: str):
        logger.info(f"Socket connection for train <{train_id}> closed: {websocket.client}")
        self.active_train_connections[train_id].remove(websocket)

    async def make_client_response(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast_for_train(self, train_id: str, message: str):
        for connection in self.active_train_connections[train_id]:
            await connection.send_text(message)
