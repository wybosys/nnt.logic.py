import traceback

import termcolor

from .logger import AbstractLogger
from ..manager import config


class Console(AbstractLogger):

    def log(self, msg, status=None):
        if config.DEVELOP or config.DEBUG:
            print(msg)

    def warn(self, msg, status=None):
        termcolor.cprint(msg, 'yellow')

    def info(self, msg, status=None):
        print(msg)

    def fatal(self, msg, status=None):
        termcolor.cprint(msg, 'red')

    def error(self, e: Exception, status=None):
        tb = e.__traceback__
        print(''.join(traceback.format_tb(tb)))
        termcolor.cprint(e, 'red')

    def exception(self, err: Exception, status=None):
        tb = err.__traceback__
        print(''.join(traceback.format_tb(tb)))
        termcolor.cprint(err, 'red')
