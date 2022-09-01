# Build a Message Bus with Redis Streams and FastAPI

Readme [also in Spanish here](./readme_spanish.md). Presentation given at [RedisConf 2020](https://www.youtube.com/watch?v=LHOjW42-A40).

## How to run the code in this repo

First install Redis, and run `redis-server`.

Use `pip` or `poetry` to install deps.

Run the server with `uvicorn src.main:app --reload --host 0.0.0.0 --port 8001`, or with `poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8001` if you're using `poetry`.

Then connect to the stream proxy ws endpoint with `websocat`, or from an empty browser tab:

```sh
websocat "ws://127.0.0.1:8001/stream/test?max_frequency=1"
```

```js
let socket = new WebSocket('ws://localhost:8001/stream/test')
socket.addEventListener('message', msg => console.log(JSON.parse(msg.data)))
```

Finally, connect to the Redis server by running `redis-cli`, and publish messages to the "test" stream, or whichever stream you want, using:

```
>127.0.0.1:6379> XADD test * greeting "hello there" from "kyle"
```

You can read more about Redis streams, and how to publish messages to them and read from them, here: <https://redis.io/topics/streams-intro>.

## About me

I'm Kyle Bebak, web architect at [Elementary Robotics](https://www.elementaryrobotics.com/). I write stuff in Python, and web app with React and TypeScript. I like biking, cooking, walking my dog, etc.

My email is kyle@elementaryrobotics.com.
