from ..config import NodeIsEnable
from ..core import app, logger
from ..core.models import STATUS
from ..server.transaction import EmptyTransaction

_servers = {}


async def Start(cfg):
    if len(cfg):
        for e in cfg:
            if not NodeIsEnable(e):
                continue
            if 'entry' not in e:
                print('server没有配置entry节点')
                continue

            t = app.App.shared().instanceEntry(e['entry'])
            if not t:
                continue

            if t.config(e):
                _servers[t.id] = t
                await t.start()
            else:
                print(t.id + "配置失败")
    else:
        Stop()


def Wait():
    for k in _servers:
        _servers[k].wait()


def Stop():
    global _servers
    for k in _servers:
        s = _servers[k]
        s.stop()
    _servers = {}


def RegisterRouter(srvid: str, obj):
    """ 直接注册router到server """
    if srvid not in _servers:
        logger.fatal("没有找到注册Router时使用的服务器 " + srvid)
        return
    srvR = _servers[srvid]
    if not srvR.routers:
        logger.fatal("该服务器 %s 不支持注册Router" % srvid)
        return
    srvR.routers.register(obj)


def FindRouter(srvid: str, action: str):
    """ 查找srv上面的router """
    if srvid not in _servers:
        logger.fatal("没有找到注册Router时使用的服务器 %s" % srvid)
        return None
    srvR = _servers[srvid]
    if not srvR.routers:
        logger.fatal("该服务器 %s 不支持注册Router" % srvid)
        return None
    ap = action.split(".")
    return srvR.routers.find(ap[0])


def Find(srvid: str, clz=None):
    """ 查找服务 """
    if srvid not in _servers:
        return None
    r = _servers[srvid]
    if clz:
        return r if isinstance(r, clz) else None
    return r


class ImpCallCalback:

    def __init__(self, srvid, action, cb):
        super().__init__()
        self.srvid = srvid
        self.action = action
        self.cb = cb

    def __call__(self, t):
        if self.t.status:
            logger.warn("调用 %s 的动作 %s 返回 %d" %
                        (self.srvid, self.action, t.status))
        self.cb(t)


def ImplCall(srvid: str, action: str, params, cb, ac=None):
    """ 直接在控制台调用api """
    srv = Find(srvid)
    if not srv:
        logger.fatal("没有找到该服务器 %s" % srvid)
        et = EmptyTransaction()
        et.status = STATUS.SERVER_NOT_FOUND
        cb(et)
        return
    if not srv.invoke:
        logger.fatal("服务器 %s 没有实现IConsoleServer接口" % srvid)
        et = EmptyTransaction()
        et.status = STATUS.ARCHITECT_DISMATCH
        cb(et)
        return
    params["action"] = action
    params["__callback"] = ImpCallCalback(srvid, action, cb)

    srv.invoke(params, None, None, ac)
