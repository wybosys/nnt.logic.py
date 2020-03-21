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


def log(str):
    print(str)


def warn(str):
    print(str)


def info(str):
    print(str)


def fatal(str):
    print(str)


def exception(e):    
    print(e)


def error(e):
    print(e)
