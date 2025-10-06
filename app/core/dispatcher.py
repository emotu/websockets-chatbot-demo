import asyncio
from typing import Callable

from rich.pretty import pprint


class DispatchManager:
    def __init__(self, listener: Callable):
        self._connections: dict[str, asyncio.Queue] = {}
        self._listener = listener
        self._incoming = asyncio.Queue(maxsize=10000)

    async def connect(self, thread_id) -> asyncio.Queue:
        queue = self._connections.setdefault(thread_id, asyncio.Queue(maxsize=1000))

        return queue

    async def receive(self, thread_id: str, message_id) -> bool:
        self._incoming.put_nowait((thread_id, message_id))
        return True

    async def send(self, thread_id, reply) -> bool:
        queue = self._connections.get(thread_id, None)
        if not queue:
            return False

        queue.put_nowait((thread_id, reply))
        return True

    async def listen(self):
        try:
            while True:
                thread_id, message_id = await self._incoming.get()
                await self._listener(self, thread_id, message_id)
        except SystemExit:
            print("Exiting")

    async def start(self):
        pprint("Starting background listener task")
        asyncio.create_task(self.listen())
