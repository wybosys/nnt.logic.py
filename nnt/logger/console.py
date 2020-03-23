from .logger import AbstractLogger
from ..manager import config
import traceback, termcolor

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

    def exception(self, err: Exception, status=None):
        tb = err.__traceback__
        print(''.join(traceback.format_tb(tb)))
        termcolor.cprint(err, 'red')
