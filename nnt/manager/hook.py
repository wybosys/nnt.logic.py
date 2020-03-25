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
