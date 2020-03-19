# -*- coding:utf-8 -*-

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
        return None

    def containsEntry(self, entry):
        return False
