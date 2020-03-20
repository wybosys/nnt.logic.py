from ..core import logger
from ..core.models import *
from ..core.python import *
from ..manager import config
from . import devops
import types

class IRouterable:

    def __init__(self):
        super().__init__()
        self.routers = None

class Routers:

    def __init__(self):
        super().__init__()
        self._routers = {}

    @property
    def length(self):
        return len(self._routers)

    def register(self, obj):
        if obj.action in self._routers:
            logger.fatal("已经注册了一个同名的路由 %s" % obj.action)
            return
        self._routers[obj.action] = obj

    def find(self, id):
        return at(self._routers, id)

    def unregister(self, act):
        delete(self._routers, act)

    def __iter__(self):
        return self._routers.__iter__()

    def toArray(self):
        return list(self._routers.values())

    async def process(self, trans):
        ac = trans.ace

        # 查找router
        r = at(self._routers, trans.router)
        if not r:
            trans.status = STATUS.ROUTER_NOT_FOUND
            trans.submit()
            return        

        # 模型化
        sta = trans.modelize(r)
        if sta:
            trans.status = sta
            trans.submit()
            return        

        # 恢复数据上下文
        await trans.collect()

        # 请求锁，实现流控的目的
        if trans.frqctl and not await trans.lock():
            trans.status = STATUS.HFDENY
            trans.submit()
            return

        # 检查是否需要验证
        if ac and ac.ignore:
            # 不做权限判断
            pass
        elif not trans.expose:
            # 访问权限判断
            if trans.needAuth():
                if not trans.auth():
                    trans.status = STATUS.NEED_AUTH
                    trans.submit()
                    return                
            else:
                # 检查devops
                if not await self._devopscheck(trans):
                    trans.status = STATUS.PERMISSIO_FAILED
                    trans.submit()
                    return

        func = at(r, trans.call)        
        if type(func) != types.FunctionType:
            trans.status = STATUS.ACTION_NOT_FOUND
            trans.submit()
            return        

        # 不论同步或者异步模式，默认认为是成功的，业务逻辑如果出错则再次设置status为对应的错误码
        trans.status = STATUS.OK
        try:
            await func(trans)            
        except Exception as err:
            if isinstance(err, ModelError):
                trans.status = err.code
                trans.message = err.message
            else:
                trans.status = STATUS.EXCEPTION
                trans.message = err.message            
            trans.submit()

    async def listen(self, trans):
        trans.timeout(-1)

        # 查找router
        r = at(self._routers, trans.router)
        if not r:
            trans.status = STATUS.ROUTER_NOT_FOUND
            trans.submit()
            return        

        # 模型化
        sta = trans.modelize(r)
        if sta:
            trans.status = sta
            trans.submit()
            return        

        trans.quiet = True
        trans.status = STATUS.OK    

    async def unlisten(self, trans):
        trans.timeout(-1)

        # 查找router
        r = at(self._routers, trans.router)
        if not r:
            trans.status = STATUS.ROUTER_NOT_FOUND
            trans.submit()
            return        

        # 模型化
        sta = trans.modelize(r)
        if sta:
            trans.status = sta
            trans.submit()
            return        

        trans.quiet = True
        trans.status = STATUS.OK    

    # devops下的权限判断
    async def _devopscheck(self, trans):
        # devops环境下才进行权限判定
        if config.LOCAL:
            return True

        # 允许客户端访的将无法进行服务端权限判定
        if config.CLIENT_ALLOW:
            return True

        # 和php等一样的规则
        if config.DEVOPS_DEVELOP:            
            skip = at(trans.params, devops.permissions.KEY_SKIPPERMISSION)
            if skip:
                return True        

        clientip = trans.info.addr
        if (!Permissions.allowClient(clientip)) {
            logger.log("设置为禁止 " + clientip + " 访问服务")
            return false
        }

        let permid = trans.params[KEY_PERMISSIONID]
        if (!permid) {
            logger.log("调用接口没有传递 permissionid")
            return false
        }

        let cfg = await Permissions.locate(permid)
        if (cfg == null) {
            logger.log("permission验证失败")
            return false
        }

        return true
    }
}

