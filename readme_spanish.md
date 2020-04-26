# Construir un Message Bus con Redis Streams y FastAPI

## Descripción

Si tienes un sistema con múltiples servicios, la comunicación es clave... Cómo, entonces, podemos comunicar de una forma confiable y rápido? Cómo podemos pasar mensajes entre nuestros servicios, o pasarlos directamente de cualquier servicio a nuestros web/mobile clients?

## Objetivo

Una manera de pasar mensajes es usar un append-only log. Este data structure tiene varias ventajas: sus mensajes están guardados en el log, así que no se pueden perder, y están ordenados por timestamp, así que la secuencia de mensajes siempre se puede reconstruir.

Resulta que Redis ahora ofrece una versión muy completa de un append-only log, [Redis Streams](https://redis.io/topics/streams-intro). Vamos a usar Redis Streams como un message bus para pasar mensajes entre servicios, y vamos a usar [aioredis](https://github.com/aio-libs/aioredis) para hacer un servicio que consume estos mensajes conforme vayan llegando.

Usaremos también FastAPI, un typed y async Python web framework, para mandar los mensajes al cliente por websockets.

Veremos conceptos de event loops en general, de asyncio en espécifico, y de cómo usar [mypy](https://mypy.readthedocs.io/en/stable/) para tener un code base que se documenta sólo.

## Cómo correr el código es este repo

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

## Sobre mí

Me llamo Kyle Bebak, soy lead web architect en [Elementary Robotics](https://www.elementaryrobotics.com/). Soy Pythonista de hueso colorado, también me la paso escribiendo aplicaciones de React con TypeScript. Me gusta andar en bici, cocinar, pasear a mi perro, etc.

Mi correo es kyle@elementaryrobotics.com.
