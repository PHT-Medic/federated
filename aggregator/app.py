from typing import List

import loguru
import uvicorn

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from aggregator.socket.connection_manager import ConnectionManager, TrainConnectionManager

app = FastAPI()

manager = ConnectionManager()

train_manager = TrainConnectionManager()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/chat/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


@app.websocket("/ws/train/{train_id}")
async def train_socket_endpoint(web_socket: WebSocket, train_id: str):
    await train_manager.connect(web_socket, train_id)
    try:
        while True:
            data = await web_socket.receive_text()
            await train_manager.make_client_response(web_socket, message="You wrote: " + data)
            await train_manager.broadcast_for_train(train_id, f"Client #{web_socket.client} says: {data}")
    except WebSocketDisconnect:
        loguru.logger.info(f"Client #{web_socket.client} disconnected")
        await train_manager.disconnect(web_socket, train_id)


if __name__ == '__main__':
    uvicorn.run("aggregator.app:app", host="127.0.0.1", port=8000, reload=True)
