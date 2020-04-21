from typing import List, Tuple, Dict
import logging

import aioredis
from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed


#
# Instantiate the logger and FastAPI app
#
logger = logging.getLogger("main")
app = FastAPI()


@app.get("/echo")
async def echo():
    return {}


@app.websocket("/echo_ws")
async def echo_ws(ws: WebSocket):
    await ws.accept()
    await ws.send_json({})


# stream_name, message_id, dict of key->value pairs in message
Message = Tuple[bytes, bytes, Dict[bytes, bytes]]


async def read_from_stream(
    redis: aioredis.Redis, stream: str, latest_id: str = None, last_n: int = None
) -> List[Message]:
    timeout_ms = 60 * 1000

    # read everything after latest_id with latest_ids arg
    if latest_id is not None:
        return await redis.xread([stream], latest_ids=[latest_id], timeout=timeout_ms)

    # read last_n messages with xrevrange and count arg
    if last_n is not None:
        messages = await redis.xrevrange(stream, count=last_n)
        return list(reversed([(stream.encode("utf-8"), *m) for m in messages]))

    # default case, read all messages going forward with xread, [stream] and timeout
    return await redis.xread([stream], timeout=timeout_ms)


@app.websocket("/stream/{stream}")
async def proxy_stream(
    ws: WebSocket, stream: str, latest_id: str = None, last_n: int = None, max_frequency: float = None
):
    await ws.accept()
    # create redis connection with aioredis.create_redis
    redis = await aioredis.create_redis("redis://127.0.0.1:6379")

    # loop for as long as client is connected and our reads don't time out, sending messages to client over websocket
    while True:
        # declare messages as a list of Message
        messages: List[Message] = []

        # handle max_frequency using latest_id
        to_read_id = latest_id
        if max_frequency is not None and latest_id is not None:
            ms_to_wait = 1000 / (max_frequency or 1)
            ts = int(latest_id.split("-")[0])
            to_read_id = f"{ts + max(0, round(ms_to_wait))}"

        # read_from_stream, and handle exception raised by this function
        try:
            messages = await read_from_stream(redis, stream, to_read_id, last_n)
        except Exception as e:
            logger.info(f"read timed out for stream {stream}, {e}")
            return

        # if we have no new messages, note that read timed out and return
        if len(messages) == 0:
            logger.info(f"no new messages, read timed out for stream {stream}")
            return

        # if we have max_frequency, assign only most recent message to messages
        if max_frequency is not None:
            messages = messages[-1:]

        # prepare messages
        prepared_messages = []
        for msg in messages:
            latest_id = msg[1].decode("utf-8")
            payload = {k.decode("utf-8"): v.decode("utf-8") for k, v in msg[2].items()}
            prepared_messages.append({"message_id": latest_id, "payload": payload})

        # send messages to client, handling (ConnectionClosed, WebSocketDisconnect) in case client has disconnected
        try:
            await ws.send_json(prepared_messages)
        except (ConnectionClosed, WebSocketDisconnect):
            logger.info(f"{ws} disconnected from stream {stream}")
            return
