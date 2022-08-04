from typing import List

import uvicorn

from loguru import logger

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from pht_federated.aggregator.socket.connection_manager import ConnectionManager, TrainConnectionManager
#from pht_federated.aggregator.socket.socket_app import socket_app

app = FastAPI()

'''
app.mount("/", socket_app)

train_manager = TrainConnectionManager()


@app.websocket("/ws/train/{train_id}")
async def train_socket_endpoint(web_socket: WebSocket, train_id: str):
    await train_manager.connect(web_socket, train_id)
    try:
        while True:
            data = await web_socket.receive_text()
            await train_manager.make_client_response(web_socket, message="You wrote: " + data)
            await train_manager.broadcast_for_train(train_id, f"Client #{web_socket.client} says: {data}")
    except WebSocketDisconnect:
        logger.info(f"Client #{web_socket.client} disconnected")
        await train_manager.disconnect(web_socket, train_id)
'''

if __name__ == '__main__':
    uvicorn.run("pht_federated.aggregator.app:app", host="127.0.0.1", port=8000, reload=True)
