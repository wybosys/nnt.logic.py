import logging
import os
import traceback
from logging.handlers import RotatingFileHandler

from .logger import AbstractLogger
from ..core import url
from ..core.models import BreakError
from ..manager import config


class File(AbstractLogger):

    def __init__(self):
        super().__init__()
        # 保存目录
        self.path = config.CACHE + '/logs'

        # 最大日志个数
        self.maxfiles = 5
        # 单个日志最大为100M
        self.maxsize = 1024 * 1024 * 100

        self._log = logging.getLogger()
        if config.DEBUG:
            self._log.setLevel(level=logging.DEBUG)
        else:
            self._log.setLevel(level=logging.INFO)

        self._err = logging.getLogger('error')
        self._err.setLevel(level=logging.INFO)

    def config(self, cfg, root=None):
        if not super().config(cfg, root):
            return False
        if 'path' in cfg:
            self.path = url.expand(cfg['path'])
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

        f = RotatingFileHandler(self.path + '/log', maxBytes=self.maxsize, backupCount=self.maxfiles)
        f.setFormatter(fmt)
        self._log.addHandler(f)

        f = RotatingFileHandler(self.path + '/err', maxBytes=self.maxsize, backupCount=self.maxfiles)
        f.setFormatter(fmt)
        self._err.addHandler(f)

        return True

    def log(self, msg, status=None):
        if config.DEVELOP or config.DEBUG:
            self._log.info(msg)

    def warn(self, msg, status=None):
        self._log.warn(msg)

    def info(self, msg, status=None):
        self._log.info(msg)

    def fatal(self, msg, status=None):
        self._err.fatal(msg)

    def error(self, err: Exception, status=None):
        if not isinstance(err, BreakError) and config.DEBUG:
            tb = err.__traceback__
            self._err.error(''.join(traceback.format_tb(tb)))
        self._err.error(err)

    def exception(self, err: Exception, status=None):
        if not isinstance(err, BreakError):
            tb = err.__traceback__
            self._err.exception(''.join(traceback.format_tb(tb)))
        self._err.exception(err)
