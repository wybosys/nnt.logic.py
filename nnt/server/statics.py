import multiprocessing

import flask

from nnt.server.server import AbstractServer
from ..core import url, logger
from ..core.python import *


class Statics(AbstractServer):

    def __init__(self):
        super().__init__()
        self._hdl: multiprocessing.Process = None

    def config(self, cfg):
        if not super().config(cfg):
            return False
        if not at(cfg, 'port'):
            return False
        self.listen = None
        if at(cfg, 'listen'):
            if cfg['listen'] == '*':
                self.listen = '0.0.0.0'
            else:
                self.listen = cfg['listen']
        else:
            self.listen = '127.0.0.1'
        self.port = cfg['port']
        if 'path' not in cfg:
            return False
        self.path = url.expand(cfg['path'])
        return True

    async def start(self):
        self._hdl = multiprocessing.Process(target=self._dostart)
        self._hdl.start()
        await super().start()
        logger.info("启动 %s@statics" % self.id)

    def _dostart(self):
        app = flask.Flask(self.id, static_folder=self.path, static_url_path='')
        app.run(host=self.listen, port=self.port)

    def stop(self):
        try:
            self._hdl.terminate()
            self._hdl.close()
        except Exception as err:
            logger.error(err)
        self._hdl = None
