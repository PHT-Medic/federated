from typing import Any

import socketio

mgr = socketio.AsyncRedisManager('redis://localhost:6379')
sio: Any = socketio.AsyncServer(async_mode="asgi", logger=True, engineio_logger=True)
socket_app = socketio.ASGIApp(sio)


@sio.on("connect")
async def connect(sid, env):
    print("on connect")


@sio.on("direct")
async def direct(sid, msg):
    print(f"direct {msg}")
    await sio.emit("event_name", msg, room=sid)  # we can send message to specific sid


@sio.on("broadcast")
async def broadcast(sid, msg):
    print(f"broadcast {msg}")
    await sio.emit("event_name", msg)  # or send to everyone


@sio.on("join_train")
async def join_train(sid, train_id):
    await sio.enter_room(sid, train_id)


@sio.on("disconnect")
async def disconnect(sid):
    print("on disconnect")

