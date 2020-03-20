from ..config import *

class Filter:
    LOG = "log"
    WARN = "warn"
    INFO = "info"
    FATAL = "fatal"
    EXCEPTION = "exception"
    ALL = "all"

    @staticmethod
    def Explode(cfg):
        r = set()        
        if cfg == Filter.ALL:
            vs = [Filter.LOG,
                Filter.WARN,
                Filter.INFO,
                Filter.FATAL,
                Filter.EXCEPTION
            ]
        else:            
            vs = Attribute.FromString(cfg)
        for e in vs:
            r.add(e)
        return r

class LoggerNode(Node):

    def __init__(self):
        super().__init__()
        self.filter = None

class AbstractLogger:

    def __init__(self):
        super().__init__()
        self._filters = set()
    

    def isAllow(self, filter):        
        return filter in self._filters

    def config(self, cfg, root = None):        
        self._filters = Filter.Explode(cfg['filter'])
        return True    

    def log(self, msg, status = None): pass    
    def warn(self, msg, status = None): pass
    def info(self, msg, status = None): pass
    def fatal(self, msg, status = None): pass
    def exception(self, msg, status = None): pass
