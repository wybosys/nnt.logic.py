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
        self.name = 'log'

        self.logger = logging.getLogger()
        if config.DEBUG:
            self.logger.setLevel(level=logging.DEBUG)
        else:
            self.logger.setLevel(level=logging.INFO)

    def config(self, cfg, root=None):
        if not super().config(cfg, root):
            return False
        if 'path' in cfg:
            self.path = url.expand(cfg['path'])
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        f = RotatingFileHandler(self.path + '/' + self.name, maxBytes=self.maxsize, backupCount=self.maxfiles)
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f.setFormatter(fmt)
        self.logger.addHandler(f)

        return True

    def log(self, msg, status=None):
        if config.DEVELOP or config.DEBUG:
            self.logger.log(msg)

    def warn(self, msg, status=None):
        self.logger.warn(msg)

    def info(self, msg, status=None):
        self.logger.info(msg)

    def fatal(self, msg, status=None):
        self.logger.fatal(msg)

    def error(self, err: Exception, status=None):
        if not isinstance(err, BreakError) and config.DEBUG:
            tb = err.__traceback__
            print(''.join(traceback.format_tb(tb)))
        self.logger.error(err)

    def exception(self, err: Exception, status=None):
        if not isinstance(err, BreakError):
            tb = err.__traceback__
            print(''.join(traceback.format_tb(tb)))
        self.logger.exception(err)
