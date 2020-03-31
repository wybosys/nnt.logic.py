import multiprocessing
import signal

import flask
import flask_compress
import gevent.pywsgi

from .server import AbstractServer
from ..core import url, logger
from ..core.python import *


class Statics(AbstractServer):

    def __init__(self):
        super().__init__()
        self._hdl: multiprocessing.Process = None

        self.listen = None
        self.port = 80
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
        self.path = os.path.abspath(url.expand(cfg['path']))
        self.prefix = at(cfg, 'prefix', self.prefix)
        return True

    async def start(self):
        self._hdl = multiprocessing.Process(target=self._dostart)
        self._hdl.start()
        await super().start()
        logger.info("启动 %s@statics" % self.id)

    def _dostart(self):
        app = flask.Flask(self.id, static_folder=self.path, static_url_path=self.prefix)
        flask_compress.Compress(app)

        # app.run(host=self.listen, port=self.port)

        @app.route('/')
        def index():
            return flask.send_from_directory(self.path, 'index.html')

        # svr = wsgiserver.CherryPyWSGIServer((self.listen, self.port), app)
        # svr.start()
        svr = gevent.pywsgi.WSGIServer((self.listen, self.port), app)
        svr.serve_forever()

        def cbstop(sig, frame):
            svr.stop()
            quit(0)

        signal.signal(signal.SIGINT, cbstop)
        signal.signal(signal.SIGTERM, cbstop)
        signal.signal(signal.SIGHUP, cbstop)

    def stop(self):
        try:
            self._hdl.terminate()
            self._hdl.wait()
        except Exception as err:
            logger.error(err)
        self._hdl = None
