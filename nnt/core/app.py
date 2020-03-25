import importlib
import signal

import termcolor

from . import signals as ss, logger

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

        def cbstop(sig, frame):
            self.stop()

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
            termcolor.cprint("导入库失败 %s" % entry, 'red')
            logger.exception(err)
        return None

    def requirePath(self, path: str) -> object:
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
