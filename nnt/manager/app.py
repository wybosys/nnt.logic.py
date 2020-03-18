# -*- coding:utf-8 -*-

import nnt.core.signals as ss

kSignalEventStarted = '::nn::app::started'
kSignalEventStopped = '::nn::app::stopped'

class App(ss.SObject):

    _shared = None

    @property
    def shared():
        return App._shared

    def __init__(self):
        super().__init__()
        App._shared = self


# 用于挂住系统进程的钩子
BOOT = 'boot'
STARTED = 'sarted'
STOPPED = 'stopped'

# 全局钩子
_hooks = {}

def Hook(step, proc):
    if step not in _hooks:
        arr = []
        _hooks[step] = arr
    else:
        arr = _hooks[step]
    arr.append(proc)

def RunHooks(step):
    if step in _hooks:
        arr = _hooks[step]
        for e in arr:
            e()

