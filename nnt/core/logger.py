class Level:
    SPECIAL = 9
    CUSTOM = 8
    DEBUG = 7
    INFO = 6
    NOTICE = 5
    WARNING = 4
    ERROR = 3
    ALERT = 2
    CRITICAL = 1
    EMERGENCE = 0
    EMERGENCY = 0


def log(s):
    print(s)


def warn(s):
    print(s)


def info(s):
    print(s)


def fatal(s):
    print(s)


def exception(e):
    print(e)


def error(e):
    print(e)


class Safe:
    """包装一个函数，当异常发生时打印为错误"""

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            self.func(*args, **kwargs)
        except Exception as err:
            error(err)
