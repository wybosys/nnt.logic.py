import multiprocessing
import signal

import flask
import gevent

from nnt.server.server import AbstractServer
from ..core import url, logger
from ..core.python import *


class Statics(AbstractServer):

    def __init__(self):
        super().__init__()
        self._hdl: multiprocessing.Process = None

        # 监听地址
        self.listen = None
        self.port = 90
        self.prefix = ''

    def config(self, cfg):
        if not super().config(cfg):
            return False
        if not at(cfg, 'port'):
            return False
        if not at(cfg, 'path'):
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
        self.path = url.expand(cfg['path'])
        self.prefix = at(cfg, 'prefix', self.prefix)
        return True

    async def start(self):
        self._hdl = multiprocessing.Process(target=self._dostart)
        self._hdl.start()
        await super().start()
        logger.info("启动 %s@statics" % self.id)

    def _dostart(self):
        app = flask.Flask(self.id, static_folder=self.path, static_url_path=self.prefix)
        app.run(host=self.listen, port=self.port)

        svr = gevent.pywsgi.WSGIServer((self.listen, self.port), app)
        svr.serve_forever()

        def cbstop(sig, frame):
            svr.stop()
            # app.stop()
            quit(0)

        signal.signal(signal.SIGINT, cbstop)
        signal.signal(signal.SIGTERM, cbstop)
        signal.signal(signal.SIGHUP, cbstop)


def stop(self):
    try:
        self._hdl.terminate()
        self._hdl.close()
    except Exception as err:
        logger.error(err)
    self._hdl = None
