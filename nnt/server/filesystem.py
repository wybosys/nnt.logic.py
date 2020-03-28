import os
import shutil

from nnt.core import logger, url
from nnt.server.server import AbstractServer


class FileSystem(AbstractServer):

    def config(self, cfg):
        super().config(cfg)
        if 'path' not in cfg:
            return False
        self.path = url.expand(cfg['path'])
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        return True

    async def start(self):
        await super().start()
        logger.info("启动 %s@rest" % self.id)

    def move(self, src, dst):
        dst = self.path + '/' + dst
        try:
            shutil.move(src, dst)
        except Exception as err:
            logger.error(err)

    def copy(self, src, dst):
        dst = self.path + '/' + dst
        try:
            shutil.copy(src, dst)
        except Exception as err:
            logger.error(err)
