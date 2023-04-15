import tempfile

import leveldb

from .kv import AbstractKv, DbExecuteStat
from ..core import url, logger
from ..core.object import Variant, VariantType


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

    def close(self):
        self._db = None

    async def get(self, key) -> Variant:
        key = key.encode('utf-8')
        d = self._db.Get(key)
        v = Variant.Unserialize(d)
        return v

    async def getraw(self, key) -> object:
        key = key.encode('utf-8')
        d = self._db.Get(key)
        return d

    async def set(self, key, val: Variant):
        key = key.encode('utf-8')
        self._db.Put(key, val.serialize())
        return True

    async def getset(self, key, val: Variant) -> Variant:
        p = await self.get(key)
        await self.set(key, val)
        return p

    async def autoinc(self, key, delta: int) -> int:
        d = await self.get(key)
        if d is None or d.typ != VariantType.NUMBER:
            await self.set(key, 0)
            return 0
        else:
            v = Variant(d.number + delta)
            await self.set(key, v)
            return v.number

    async def inc(self, key, delta: int) -> int:
        d = await self.get(key)
        if not d or d.typ != VariantType.NUMBER:
            await self.set(key, 0)
            return 0
        else:
            v = Variant(d.number + delta)
            await self.set(key, v)
            return v.number

    async def delete(self, key) -> DbExecuteStat:
        key = key.encode('utf-8')
        self._db.Delete(key)
        return DbExecuteStat(remove=1)
