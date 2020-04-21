## Construir un realtime message bus usando Redis y asyncio

## Descripción
Si tienes un sistema con múltiples servicios, la comunicación es clave... Cómo, entonces, podemos comunicar de una forma confiable y rápido? Cómo podemos pasar mensajes entre nuestros servicios, o pasarlos directamente de cualquier servicio a nuestros web/mobile clients?

## Objetivo
Una manera de pasar mensajes es usar un append-only log. Este data structure tiene varias ventajas: sus mensajes están guardados en el log, así que no se pueden perder, y están ordenados por timestamp, así que la secuencia de mensajes siempre se puede reconstruir.

Resulta que Redis ahora ofrece una versión muy completa de un append-only log, [Redis Streams](https://redis.io/topics/streams-intro). Vamos a usar Redis Streams como un message bus para pasar mensajes entre servicios, y vamos a usar [aio-redis](https://github.com/aio-libs/aioredis) para hacer un servicio que consume estos mensajes conforme vayan llegando.

Usaremos también FastAPI, un typed y async Python web framework, para mandar los mensajes al cliente por websockets.

Veremos conceptos de event loops en general, de asyncio en espécifico, y de cómo usar [mypy](https://mypy.readthedocs.io/en/stable/) para tener un code base que se documenta sólo.

## Sobre mí
Me llamo Kyle Bebak, soy lead web architect en Elementary Robotics. Soy Pythonista de hueso colorado, también me la paso escribiendo aplicaciones de React con TypeScript. Me gusta andar en bici, cocinar, pasear a mi perro, etc.

Mi correo es kylebebak@gmail.com.
