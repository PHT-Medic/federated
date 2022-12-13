from typing import List

import uvicorn

from loguru import logger

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware

from pht_federated.aggregator.api.api import api_router
from pht_federated.aggregator.socket.connection_manager import ConnectionManager, TrainConnectionManager
#from pht_federated.aggregator.socket.socket_app import socket_app
from pht_federated.aggregator.storage.db.setup_db import setup_db

app = FastAPI(
    title="PHT - Federated", docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/v1/openapi.json"
)

origins = [
    "http://localhost:8080",
    "http://localhost:8080/",
    "http://localhost:8081",
    # "http://localhost:3000",
    # "http://localhost",
    "*"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    logger.info("Setting up database...")
    setup_db()

if __name__ == '__main__':
    uvicorn.run("pht_federated.aggregator.app:app", host="127.0.0.1", port=8000, reload=True)
