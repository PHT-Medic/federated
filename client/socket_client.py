import asyncio
import socketio
from loguru import logger

sio = socketio.AsyncClient()


@sio.event
async def join_train_room(train_id):
    logger.info("Joined train room {}".format(train_id))
    await sio.emit("join_train", train_id)
    return train_id


@sio.event
async def connect():
    logger.info("Connected to server")
    print('connection established')


@sio.event
async def my_message(data):
    print('message received with ', data)
    await sio.emit('my response', {'response': 'my response'})


@sio.event
async def round_ready(data):
    print('round_ready received with ', data)


@sio.event
async def disconnect():
    print('disconnected from server')


async def main():
    await sio.connect('http://localhost:8000')
    await sio.emit("join_train_room", "1")
    await sio.wait()



if __name__ == '__main__':
    asyncio.run(main())
