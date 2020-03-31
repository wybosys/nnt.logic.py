import subprocess

from .server import AbstractServer
from ..core import url, logger
from ..core.python import *


class VueErp(AbstractServer):

    def __init__(self):
        super().__init__()

        self.listen = None
        self.port = 80
        self.path = None

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
        return True

    async def start(self):
        env = {'HOST': self.listen,
               'PORT': str(self.port),
               'VERBOSE': 'false',
               'SOURCEMAP': 'false'
               }
        cmd = 'npm run dev --scripts-prepend-node-path'
        self._hdl = subprocess.Popen(cmd, shell=True, cwd=self.path, env=env, stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE)
        await super().start()
        logger.info("启动 %s@statics" % self.id)

    def stop(self):
        try:
            self._hdl.terminate()
            self._hdl.wait()
        except Exception as err:
            logger.error(err)
        self._hdl = None
