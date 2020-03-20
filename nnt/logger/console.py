from .logger import AbstractLogger
from ..manager import config


class Console(AbstractLogger):

    def log(self, msg, status=None):
        if config.DEVELOP or config.DEBUG:
            print(msg)

    def warn(self, msg, status=None):
        print(msg)

    def info(self, msg, status=None):
        print(msg)

    def fatal(self, msg, status=None):
        print(msg)

    def exception(self, msg, status=None):
        print(msg)
