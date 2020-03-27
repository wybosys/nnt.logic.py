import threading
import time

MINUTE = 60
MINUTE_2 = 120
MINUTE_3 = 180
MINUTE_4 = 240
MINUTE_5 = 300
MINUTE_15 = 900
MINUTE_30 = 1800
HOUR = 3600
HOUR_2 = 7200
HOUR_6 = 21600
HOUR_12 = 43200
DAY = 86400
WEEK = 604800
MONTH = 2592000
YEAR = 31104000


class DateTime:

    @staticmethod
    def Now() -> float:
        """ 获取当前时间戳，默认整个环境中单位为秒, 如果环节中强制只能为int，则对应用的地方再转换成int，否则默认都是float，避免排序时丧失精度"""
        # timestamp没有时区的概念
        return time.time()

    @staticmethod
    def Current() -> int:
        """int形式的时间戳"""
        return int(time.time())


class Delayer:

    def __init__(self, seconds, func):
        super().__init__()
        self.interval = seconds
        self.func = func
        self._tmr = None

    def start(self):
        if self._tmr:
            print("正在执行延迟")
            return
        self._tmr = threading.Timer(interval=self.interval, function=self.func)
        self._tmr.start()
        return self

    def stop(self):
        if not self._tmr:
            print("没有执行延迟")
            return
        self._tmr.cancel()
        self._tmr = None
        return self


class Timer:
    """定时器"""

    def __init__(self, interval, target, repeat=1, args=None):
        super().__init__()
        self._interval = interval
        self._target = target
        self._repeat = repeat
        self._args = args if args is not None else []
        self._tmr = None

    def start(self):
        if self._tmr:
            print("定时器已经启动")
            return
        self._dostart()

    def _dostart(self):
        self._tmr = threading.Timer(self._interval, self._dotick)
        self._cur = 0
        self._tmr.start()

    def _dotick(self):
        self._target(*self._args)
        if self._repeat != -1:
            self._cur += 1
            if self._cur >= self._repeat:
                self._dostop()
                return
        self._dostart()

    def stop(self):
        if not self._tmr:
            return
        self._dostop()

    def _dostop(self):
        self._tmr.cancel()
        self._tmr = None

    @property
    def interval(self):
        return self._interval

    @property
    def target(self):
        return self._target

    @property
    def repeat(self):
        return self._repeat


class Const(object):
    """增加Const的支持"""

    def __init__(self, defs=None):
        super().__init__()
        if type(defs) == dict:
            for k in defs:
                setattr(self, k, defs[k])
        elif type(defs) == list:
            for k in defs:
                setattr(self, str(k), k)

    def __setattr__(self, key, value):
        if self.__dict__.has_key(key):
            raise "Changing const.%s" % key
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        if self.__dict__.has_key(key):
            return self.key
        else:
            return None
