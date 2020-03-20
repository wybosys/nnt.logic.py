import datetime, time

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
    