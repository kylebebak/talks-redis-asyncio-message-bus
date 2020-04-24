from typing import List, Tuple, Dict
import logging

import aioredis
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed


#
# Instantiate the logger and FastAPI app
#
logger = logging.getLogger("main")
app = FastAPI()

# Allow CORS for requests coming from any domain
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


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
    redis: aioredis.Redis, stream: str, latest_id: str = None, past_ms: int = None, last_n: int = None
) -> List[Message]:
    timeout_ms = 60 * 1000

    # Blocking read for every message added after latest_id, using XREAD
    if latest_id is not None:
        return await redis.xread([stream], latest_ids=[latest_id], timeout=timeout_ms)

    # Blocking read for every message added after current timestamp minus past_ms, using XREAD
    if past_ms is not None:
        server_time_s = await redis.time()
        latest_id = str(round(server_time_s * 1000 - past_ms))
        return await redis.xread([stream], latest_ids=[latest_id], timeout=timeout_ms)

    # Non-blocking read for last_n messages, using XREVRANGE
    if last_n is not None:
        messages = await redis.xrevrange(stream, count=last_n)
        return list(reversed([(stream.encode("utf-8"), *m) for m in messages]))

    # Default case, blocking read for all messages added after calling XREAD
    return await redis.xread([stream], timeout=timeout_ms)


@app.websocket("/stream/{stream}")
async def proxy_stream(
    ws: WebSocket,
    stream: str,
    latest_id: str = None,
    past_ms: int = None,
    last_n: int = None,
    max_frequency: float = None,
):
    await ws.accept()
    # Create redis connection with aioredis.create_redis
    redis = await aioredis.create_redis("redis://127.0.0.1:6379")

    # Loop for as long as client is connected and our reads don't time out, sending messages to client over websocket
    while True:
        # Limit max_frequency of messages read by constructing our own latest_id
        to_read_id = latest_id
        if max_frequency is not None and latest_id is not None:
            ms_to_wait = 1000 / (max_frequency or 1)
            ts = int(latest_id.split("-")[0])
            to_read_id = f"{ts + max(0, round(ms_to_wait))}"

        # Call read_from_stream, and return if it raises an exception
        messages: List[Message]
        try:
            messages = await read_from_stream(redis, stream, to_read_id, past_ms, last_n)
        except Exception as e:
            logger.info(f"read timed out for stream {stream}, {e}")
            return

        # If we have no new messages, note that read timed out and return
        if len(messages) == 0:
            logger.info(f"no new messages, read timed out for stream {stream}")
            return

        # If we have max_frequency, assign only most recent message to messages
        if max_frequency is not None:
            messages = messages[-1:]

        # Prepare messages (message_id and JSON-serializable payload dict)
        prepared_messages = []
        for msg in messages:
            latest_id = msg[1].decode("utf-8")
            payload = {k.decode("utf-8"): v.decode("utf-8") for k, v in msg[2].items()}
            prepared_messages.append({"message_id": latest_id, "payload": payload})

        # Send messages to client, handling (ConnectionClosed, WebSocketDisconnect) in case client has disconnected
        try:
            await ws.send_json(prepared_messages)
        except (ConnectionClosed, WebSocketDisconnect):
            logger.info(f"{ws} disconnected from stream {stream}")
            return
