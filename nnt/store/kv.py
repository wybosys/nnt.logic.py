from .store import *
from ..core.object import Variant


class AbstractKv(AbstractDbms):

    async def get(self, key) -> Variant:
        """ cb (variant):void """
        pass

    async def set(self, key, val: Variant) -> bool:
        """ val: Variant, cb: (res: boolean) => void): void """
        pass

    async def getset(self, key, val: Variant) -> Variant:
        """ val: Variant, cb: (res: Variant) => void """
        pass

    async def getraw(self, key) -> object:
        """和get的不同为返回数据库中的原始数据而不是被Var包装过的"""
        pass

    async def delete(self, key) -> DbExecuteStat:
        """ cb: (res: DbExecuteStat) => void """
        pass

    async def autoinc(self, key, delta: int) -> int:
        """ kv数据库通常没有自增函数，所以需要各个业务类自己实现
        cb: (res: DbExecuteStat) => void """
        pass

    async def inc(self, key, delta: int) -> int:
        """ cb: (id: number) => void """
        pass


class AbstractNosql(AbstractKv):

    def innerId(self, rcd):
        """ 获得记录的内部id """
        pass

    async def query(self, page, cmd, limit, skip, t):
        """ @page 数据分片，mongo中叫collection
        @cmd 查询指令 """
        pass

    async def count(self, page, cmd):
        """ 统计数量 """
        pass

    async def aggregate(self, page, cmd, process):
        """ 集合 """
        pass

    def iterate(self, page, cmd, process):
        """ 迭代 """
        pass

    async def insert(self, page, cmd):
        """ 增加新纪录 """
        pass

    async def modify(self, page, cmd):
        """ 更新
        @iid innerId 如果有的话，则直接通过iid更新，否则cmd中需要写明更新规则 """
        pass

    async def modifyone(self, page, iid, cmd):
        pass

    async def update(self, page, cmd):
        pass

    async def updateone(self, page, iid, cmd):
        pass

    async def remove(self, page, cmd):
        pass

    async def removeone(self, page, iid, cmd):
        pass
