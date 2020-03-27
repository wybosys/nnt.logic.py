# 定义了数据库访问路径，[dbid].[table].[other] 例如 kv.users
from nnt.core import logger
from nnt.manager.dbmss import Find
from nnt.store.kv import AbstractNosql, AbstractKv
from nnt.store.proto import GetTableInfo, GetFieldInfos, Decode
from nnt.store.rdb import AbstractRdb

StorePath = str
RedirectClass = type


# 数据库事务定义为通过数据库模型来访问数据
# 提供数据库的配置：dbid代表数据库服务的id，clazz代表数据库orm
# 通过TransactionDef来支持如下几种访问方式
# Clazz(可以通过@table来提供dbid)
# Clazz和dbid来定义返回的类型和dbid
# Clazz和dbClazz来定义返回的类型和提供dbid的类型
# dbid和Clazz来定义（支持运行中修改db连接的对象）

class ITransaction:

    def columns(self) -> [str]:
        """ 获取当前模型的字段列表 """
        pass


class Transaction(ITransaction):

    def __init__(self, cfg):
        super().__init__()

        if type(cfg) == tuple:
            if type(cfg[0]) == str:
                self.clazz = cfg[1]
                if not self._parseClazz(self.clazz):
                    raise TypeError("数据错误")
                self.dbid = cfg[0]
            elif type(cfg[1]) == str:
                self.clazz = cfg[0]
                if not self._parseStorePath(cfg[1]):
                    raise TypeError("数据错误")
            else:
                self.clazz = cfg[0]
                if not self._parseClazz(cfg[1]):
                    raise TypeError("数据错误")
        else:
            self.clazz = cfg
            if not self._parseClazz(self.clazz):
                raise TypeError("数据错误")

        db = Find(self.dbid)
        if db is None:
            raise TypeError("没有找到 %s 对应的数据库" % self.dbid)

        self._db = db
        if isinstance(db, AbstractRdb):
            self._rdb = db
        elif isinstance(db, AbstractNosql):
            self._nosql = db
        elif isinstance(db, AbstractKv):
            self._kv = db

    def _parseStorePath(self, sp: str) -> bool:
        ps = sp.split(".")
        if len(ps) != 2:
            return False
        self.dbid = ps[0]
        self.table = ps[1]
        return True

    def _parseClazz(self, clz) -> bool:
        ti = GetTableInfo(clz)
        if not ti:
            logger.fatal("%s 不是有效的数据库模型", clz.__name__)
            return False
        self.dbid = ti.id
        self.table = ti.table
        return True

    def columns(self) -> [str]:
        """  存储类的字段列表 """
        fps = GetFieldInfos(self.clazz)
        return list(fps.keys())

    def produce(self, res) -> object:
        """ 生成对象 """
        r = self.clazz()
        Decode(r, res)
        return r

    def close(self):
        pass
