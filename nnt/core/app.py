import importlib
from . import signals as ss

kSignalAppStarted = '::nn::app::started'
kSignalAppStopped = '::nn::app::stopped'

class App(ss.SObject):

    _shared = None

    @staticmethod
    def shared():
        return App._shared
    
    def __init__(self):
        super().__init__()
        self.signals.register(kSignalAppStarted)
        self.signals.register(kSignalAppStopped)
        App._shared = self  

    async def start(self):
        self.signals.emit(kSignalAppStarted)        

    async def stop(self):
        self.signals.emit(kSignalAppStopped)

    def instanceEntry(self, entry):
        # 形式为 xx.xx.Xxxx 约定全小写为包文件目录，最后一个为类名
        pack = entry.lower()
        try:
            mod = importlib.import_module(pack)
            _,_, clazz = entry.rpartition('.')
            func = getattr(mod, clazz)
            return func()
        except Exception as err:
            print("实例化失败 %s" % entry)
            print(err)
        return None

    def containsEntry(self, entry):
        pack = entry.lower()
        try:
            mod = importlib.import_module(pack)
            _,_, clazz = entry.rpartition('.')
            return hasattr(mod, clazz)
        except:
            pass
        return False
