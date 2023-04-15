import asyncio

import tornado
import tornado.httpserver
import tornado.process

from nnt.server import Rest


class HttpServer:
    _hdl: tornado.httpserver.HTTPServer

    def __init__(self, rest: Rest):
        self._rest = rest

    async def start(self):
        tornado.process.fork_processes(0)

        async def worker():
            self._hdl = tornado.httpserver.HTTPServer()
            self._hdl.listen(address=self._rest.listen, port=self._rest.port)
            await asyncio.Event().wait()

        asyncio.run(worker())

    async def stop(self):
        await self._hdl.close_all_connections()
