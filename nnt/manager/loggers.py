# -*- coding:utf-8 -*-

from ..core import logger

loggers = []

class TYPE:
    LOG = 0
    WARN = 1
    INFO = 2
    FATAL = 3
    EXCEPTION = 4

def output(msg, filter, typ):
    for e in loggers:    
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


