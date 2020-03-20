import redis, os
from .kv import *
from ..core.python import *
from ..core import logger
from ..core.object import *

class RedisNode:

    def __init__(self):
        super().__init__()
    
        # 是否是集群模式
        self.cluster = False

        # redis的数据库索引，注意如果redis是cluster模式，则该参数无效
        self.dbid = 0

        # 服务器地址
        self.host = None

        # 密码
        self.password = None

OPS_LIST = "list"
OPS_SET = "set"

OPS = [
    OPS_LIST,
    OPS_SET
]

class KvRedis(AbstractKv):

    def __init__(self):
        super().__init__()

        self.dbid = 0
        self.host = None
        self.port = 6379
        self.passwd = None
        self._hdl = None

    def config(self, cfg):
        if not super().config(cfg):
            return False
        if not at(cfg, 'host'):
            return False
        if not at(cfg, 'cluster'):
            self.dbid = 0
        else:
            self.dbid = at(cfg, 'dbid', 0)
        arr = cfg['host'].split(":")
        self.host = arr[0]
        if len(arr) == 2:
            self.port = int(arr[1])
        self.passwd = at(cfg, 'password')
        return True        

    async def open(self):
        self._hdl = redis.Redis(host=self.host, port=self.port, password=self.passwd)
        logger.info("连接 %s@redis" % self.id)

    async def close(self):
        self._hdl.close()
        self._hdl = None

    def select(self, dbid, cb):
        res = self._hdl.execute_command('select %d' % dbid)
        cb(res)

    def get(self, key, cb):
        res = self._hdl.get(key)
        cb(Variant.Unserialize(res))    

    def getraw(self, key, cb):
        res = self._hdl.get(key)
        cb(res)

    def delete(self, key, cb):
        res = self._hdl.delete(key)
        cb(DbExecuteStat(remove=1 if res else 0))

    def autoinc(self, key, delta, cb):
        res = self._hdl.incr(key, delta)
        cb(res)    

    def inc(self, key, delta, cb):
        res = self._hdl.incr(key, delta)
        cb(res)    
    
    def acquirelock(self, key, ttl, cb):
        pid = str(os.getpid())
        key = "locker." + key
        res = self._hdl.setnx(key, pid)
        if res:
            if res != 1:
                cb(False)
                return
            if ttl:
                self._hdl.expire(key, ttl)
            cb(True)
        else:
            cb(False)

    def releaselock(self, key, cb, force = False):
        """ 只能释放当前进程自己创建的锁, force = true, 则直接释放锁，不管是不是当前进程创建的 """
        pid = str(os.getpid())
        key = "locker." + key
        res = self._hdl.get(key)
        if force or pid == res:
            self._hdl.delete(key)
            cb(True)
            return
        cb(False)
