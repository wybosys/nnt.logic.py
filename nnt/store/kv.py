# -*- coding:utf-8 -*-

from .store import AbstractDbms

class AbstractKv(AbstractDbms):

    def get(self, key, cb): 
        """ cb (variant):void """
        pass

    def set(self, key, val, cb):
        """ val: Variant, cb: (res: boolean) => void): void """
        pass

    def getset(self, key, val):
        """ val: Variant, cb: (res: Variant) => void """
        pass

    def delete(self, key, cb):
        """ cb: (res: DbExecuteStat) => void """
        pass
    
    def autoinc(self, key, delta, cb):
        """ kv数据库通常没有自增函数，所以需要各个业务类自己实现
        cb: (res: DbExecuteStat) => void """
        pass
    
    def inc(self, key, delta, cb):
        """ cb: (id: number) => void """
        pass

class AbstractNosql(AbstractKv):

    def translate(self, filter):
        """  将filter转换成数据库查询的命令 """
        pass
    
    def innerId(self, rcd):
        """ 获得记录的内部id """
        pass
    
    def query(self, page, cmd, limit, skip, t, cb):
        """ @page 数据分片，mongo中叫collection
        @cmd 查询指令 """
        pass

    def count(self, page, cmd, cb):
        """ 统计数量 """
        pass

    def aggregate(self, page, cmd, cb, process):
        """ 集合 """
        pass

    def iterate(self, page, cmd, process):
        """ 迭代 """
        pass

    def insert(self, page, cmd, cb):
        """ 增加新纪录 """
        pass

    def modify(self, page, cmd, cb):
        """ 更新
        @iid innerId 如果有的话，则直接通过iid更新，否则cmd中需要写明更新规则 """
        pass

    def modifyone(self, page, iid, cmd, cb):
        pass
     
    def update(self, page, cmd, cb):
        pass

    def updateone(self, page, iid, cmd, cb):
        pass

    def remove(self, page, cmd, cb):
        pass

    def removeone(self, page, iid, cmd, cb):
        pass
