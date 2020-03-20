from ...store import KvRedis
from ...core.kernel import *
from ...core import logger
from ...manager import config, app
import netaddr, json, os
import asyncio.futures as futures

class _Permissions:

    def __init__(self):
        super().__init__()

        self._id = None
        self._allow = None
        self._deny = None

        # 连接devops数据库
        db = KvRedis()
        db.config({
            'id': "devops-redis",
            'entry': "nnt.store.KvRedis",
            'host': 'localhost:26379'
        })
        db.open()
        db.select(REDIS_PERMISSIONIDS)
        self._db = db

    @property
    def id(self):
        if not self._id:
            if os.path.exists('/work/run/permission.cfg'):
                jsobj = json.load(open('/work/run/permission.cfg'))
                self._id = jsobj['id']
            else:
                logger.warn("没有获取到permissionid")                    
        return self._id    

    async def locate(self, permid):
        if not self._db:
            return None
        fur = futures.Future()
        def _(res):
            fur.set_result(toJsonObject(res))
            fur.done()
        self._db.getraw(permid, _)

    def allowClient(self, clientip):
        return True

Permissions = None

def _():
    global Permissions
    if config.DEVOPS:
        Permissions = _Permissions()

app.Hook(app.STARTED, _)

KEY_PERMISSIONID = "_permissionid"
KEY_SKIPPERMISSION = "_skippermission"
REDIS_PERMISSIONIDS = 17
