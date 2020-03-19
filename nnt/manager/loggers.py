# -*- coding:utf-8 -*-

from ..core import logger
from ..logger.logger import Filter
from ..config.config import NodeIsEnable
from ..core.app import App
from ..manager import config

_loggers = []

class TYPE:
    LOG = 0
    WARN = 1
    INFO = 2
    FATAL = 3
    EXCEPTION = 4

def output(msg, filter, typ):
    for e in _loggers:    
        if e.isAllow(filter):
            if typ == TYPE.LOG:
                e.log(msg)
            elif typ == TYPE.INFO:
                e.info(msg)
            elif typ == TYPE.WARN:
                e.warn(msg)
            elif typ == TYPE.EXCEPTION:
                e.exception(msg)
            else:
                e.fatal(msg)        

def _(msg):
    if len(_loggers):
        output(msg, Filter.LOG, TYPE.LOG)
    else:
        print(msg)
logger.log = _

def _(msg):
    if len(_loggers):
        output(msg, Filter.WARN, TYPE.WARN)
    else:
        print(msg)
logger.warn = _

def _(msg):
    if len(_loggers):
        output(msg, Filter.INFO, TYPE.INFO)
    else:
        print(msg)
logger.info = _

def _(msg):
    if len(_loggers):
        output(msg, Filter.FATAL, TYPE.FATAL)
    else:
        print(msg)
logger.fatal = _

def _(msg):
    if len(_loggers):
        output(msg, Filter.EXCEPTION, TYPE.EXCEPTION)
    else:
        print(msg)
logger.exception = _

async def Start(cfg):
    if len(cfg):
        for e in cfg:            
            if not NodeIsEnable(e):
                continue
            if 'entry' not in e:
                continue

            t = App.shared().instanceEntry(e['entry'])
            if not t:
                continue

            try:
                t.config(e)
                print("输出log至 %s" % e['id'])
            except Exception as err:
                print(err)
            finally:
                _loggers.append(t)

        # 额外如果位于devops环境中，需要自动初始化devops的日志
        if config.DEVOPS:
            t = App.shared().instanceEntry("nnt.logger.Log4devops")
            t.config({
                'id': "devops-logs",
                'filter': "all"
            })
            _loggers.append(t)
    else:
        await Stop()

async def Stop():
    _loggers.clear()
