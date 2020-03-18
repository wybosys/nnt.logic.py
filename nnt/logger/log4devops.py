# -*- coding:utf-8 -*-

from .logger import AbstractLogger
from ..core.time import DateTime
from ..core.models import STATUS
from ..core.kernel import toJson
import redis
import os
import socket

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

class Log4devops(AbstractLogger):
    """当运行于devops环境中，需要按照统一的规则保存日志"""

    def __init__(self):
        super().__init__()        

        # 连接日志数据库
        hdl = redis.Redis(host="logs", port=6379,
                          retry_on_timeout=True, decode_responses=True)
        print("连接 devops-logs@redis")
        self._hdl = hdl

        # 主机日志key
        self._key = socket.gethostname()

    def config(self, cfg):
        return super().config(cfg)

    def log(self, msg, status=None):
        self.output(DEBUG, msg, status)

    def warn(self, msg, status=None):
        self.output(WARNING, msg, status)

    def info(self, msg, status=None):
        self.output(INFO, msg, status)

    def fatal(self, msg, status=None):
        self.output(CRITICAL, msg, status)

    def exception(self, msg, status=None):
        self.output(EMERGENCE, msg, status)

    def output(self, level, msg, status):
        if not self._hdl:
            print("logs日志数据库没有连接")
            return

        data = {
            't': DateTime.Current(),
            'c': STATUS.OK if status == None else status,
            'm': msg,
            'l': level
        }
        self._hdl.lpush(self._key, toJson(data))
