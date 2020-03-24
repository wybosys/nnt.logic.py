from ..core import url, logger
from ..core.object import Variant, VariantType
from .kv import AbstractKv, DbExecuteStat
import leveldb
import os
import tempfile


class KvLevelNode:

    def __init__(self):
        # 数据库保存的位置
        self.file = None


class KvLevel(AbstractKv):

    def __init__(self):
        super().__init__()
        self._db: leveldb.LevelDB = None
        self._file = None

    def config(self, cfg):
        super().config(cfg)
        self._file = url.expand(cfg['file'])
        return True

    async def open(self):
        if not self._file:
            t = tempfile.NamedTemporaryFile()
            self._file = t.name
            t.close()
        self._db = leveldb.LevelDB(self._file)
        logger.info("打开 %s@level" % self.id)

    async def close(self):
        self._db = None

    def get(self, key, cb):
        key = key.encode('utf-8')
        try:
            d = self._db.Get(key)
            v = Variant.Unserialize(d)
            cb(v)
        except:
            cb(None)

    def set(self, key, val, cb):
        key = key.encode('utf-8')
        self._db.Put(key, val.serialize())
        cb(True)

    def getset(self, key, val, cb):
        def _(d):
            self.set(val)
            cb(d)
        self.get(key, _)

    def autoinc(self, key, delta, cb):
        def _(d):
            if d == None:
                self.set(key, 0)
                cb(0)
            else:
                v = Variant(d.number + delta)
                self.set(key, v)
                cb(v.number)
        self.get(key, _)

    def inc(self, key, delta, cb):
        def _(d):
            if d == None or d.typ != VariantType.NUMBER:
                cb(None)
            else:
                v = Variant(d.number + delta)
                self.set(key, v)
                cb(v.number)
        self.get(key, _)

    def delete(self, key, cb):
        key = key.encode('utf-8')
        self._db.Delete(key)
        cb(DbExecuteStat(remove=1))
