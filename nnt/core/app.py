import importlib
import os
import shelve
import signal

import termcolor

from . import signals as ss, logger
from .kernel import uuid

kSignalAppStarted = '::nn::app::started'
kSignalAppStopped = '::nn::app::stopped'


class App(ss.SObject):
    _shared = None

    @staticmethod
    def shared() -> 'App':
        return App._shared

    def __init__(self):
        super().__init__()
        self.signals.register(kSignalAppStarted)
        self.signals.register(kSignalAppStopped)
        App._shared = self

        # 配置文件目录
        if not os.path.exists('.n2'):
            os.makedirs('.n2')

        # 配置数据库
        self._db = shelve.open('.n2/db', writeback=True)

        # 服务唯一id
        self._uniqueIdentifier = None

        def cbstop(sig, frame):
            self.stop()
            quit(0)

        signal.signal(signal.SIGINT, cbstop)
        signal.signal(signal.SIGTERM, cbstop)
        signal.signal(signal.SIGHUP, cbstop)

    async def start(self):
        self.signals.emit(kSignalAppStarted)

    def stop(self):
        self.signals.emit(kSignalAppStopped)

    def instanceEntry(self, entry) -> object:
        # 形式为 xx.xx.Xxxx 约定全小写为包文件目录，最后一个为类名
        pack = entry.lower()
        try:
            mod = importlib.import_module(pack)
            _, _, clazz = entry.rpartition('.')
            func = getattr(mod, clazz)
            return func()
        except Exception as err:
            termcolor.cprint("实例化失败 %s" % entry, 'red')
            logger.exception(err)
        return None

    def requireEntry(self, entry) -> object:
        pack = entry.lower()
        try:
            mod = importlib.import_module(pack)
            _, _, clazz = entry.rpartition('.')
            func = getattr(mod, clazz)
            return func
        except Exception as err:
            termcolor.cprint("导入实体失败 %s" % entry, 'red')
            logger.exception(err)
        return None

    def requireModule(self, module) -> object:
        try:
            mod = importlib.import_module(module)
            return mod
        except Exception as err:
            termcolor.cprint("导入库失败 %s" % module, 'red')
            logger.exception(err)
        return None

    def containsEntry(self, entry) -> bool:
        pack = entry.lower()
        try:
            mod = importlib.import_module(pack)
            _, _, clazz = entry.rpartition('.')
            return hasattr(mod, clazz)
        except:
            pass
        return False

    def uniqueIdentifier(self, idr='uniqueIdentifier') -> str:
        if idr == 'uniqueIdentifier':
            if not self._uniqueIdentifier:
                if idr not in self._db:
                    self._db[idr] = uuid()
                self._uniqueIdentifier = self._db[idr]
            return self._uniqueIdentifier
        if idr not in self._db:
            self._db[idr] = uuid()
        return self._db[idr]
