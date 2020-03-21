import datetime, time, threading

class DateTime:

    @staticmethod
    def Now():
        """ 获取当前时间戳，默认整个环境中单位为秒, 如果环节中强制只能为int，则对应用的地方再转换成int，否则默认都是float，避免排序时丧失精度"""
        # timestamp没有时区的概念
        return time.time()

    @staticmethod
    def Current():
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