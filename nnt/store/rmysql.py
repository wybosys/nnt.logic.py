# import mysql
# import mysql.connector
import sqlalchemy as alc
import sqlalchemy.dialects.mysql.types as mysqltypes
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, Query, scoped_session

from nnt.store.rdb import AbstractRdb
from .filter import Filter
from .proto import FieldOption, FpIsTypeEqual, GetFieldInfos, Fill, _GetFieldOption, Output, \
    ClearTableChangeds, GetTableInfo, GetTableChangeds, GetTablePrimary
from .session import AbstractSession
from .store import DbExecuteStat
from ..core import logger
from ..core.kernel import toInt
from ..core.models import ROWS_LIMIT
from ..core.python import *


class MySqlNode:

    def __init__(self):
        # 地址或者sock
        self.host: str = None

        # 用户、密码
        self.user: str = None
        self.pwd: str = None

        # 数据库
        self.scheme: str = None


DEFAULT_PORT = 3306


class RMySql(AbstractRdb):

    def __init__(self):
        super().__init__()
        # self._pool: mysql.connector.MySQLConnection = None
        # self._poolidr = uuid()

        self._hdl: Session = None

        # 主机名
        self.host: str = None
        self.port: int = None

        # 使用sock文件来连接
        self.sock: str = None

        # 用户名、密码
        self.user: str = None
        self.pwd: str = None
        self.scheme: str = None

    def config(self, cfg: dict) -> bool:
        super().config(cfg)

        self.user = at(cfg, 'user')
        self.pwd = at(cfg, 'pwd')
        self.scheme = at(cfg, 'scheme')
        self.host = self.sock = None

        host: str = at(cfg, 'host')
        if host is None:
            return False

        if host.startswith("unix://"):
            self.sock = host
        else:
            p = host.split(":")
            if len(p) == 1:
                self.host = host;
                self.port = DEFAULT_PORT
            else:
                self.host = p[0]
                self.port = toInt(p[1], DEFAULT_PORT)
        return True

    async def open(self):
        # dbcfg = {
        #    'database': self.scheme,
        #    'user': self.user,
        #    'password': self.pwd,
        #    'host': self.host,
        #    'port': self.port,
        #    'unix_socket': self.sock,
        #    'pool_name': self._poolidr
        # }
        try:
            # self._pool = mysql.connector.connect(**dbcfg)
            cntstr = 'mysql+mysqlconnector://'
            if self.user:
                cntstr += self.user + ':' + self.pwd + '@'
            if self.sock:
                cntstr += self.sock + '/'
            else:
                cntstr += self.host + ':' + str(self.port) + '/'
            cntstr += self.scheme
            self._hdl = alc.create_engine(cntstr)
            self._ses = scoped_session(sessionmaker(bind=self._hdl))
            logger.info('启动 mysql@%s' % self.id)
        except Exception as err:
            logger.exception(err)
            logger.fatal('启动失败 mysql@%s %s' % (self.id, cntstr))

    def close(self):
        # if self._pool:
        #    self._pool.close()
        #    self._pool = None
        if self._hdl:
            self._hdl = None

    @staticmethod
    def ConvertFpFromMysql(typ: str) -> FieldOption:
        r = FieldOption()
        if typ == "tinyint(1)":
            r.boolean = True
        elif 'int' in typ:
            r.integer = True
        elif 'char' in typ:
            r.string = True
        elif typ == "text":
            r.string = True
        return r

    def compareFieldDef(self, my: FieldOption, tgt: dict) -> bool:
        if not FpIsTypeEqual(RMySql.ConvertFpFromMysql(tgt["Type"]), my):
            return False
        if not my.key:
            if (tgt["Null"] == "NO") != my.notnull:
                return False
        if (tgt["Key"] == "PRI") != my.key:
            return False
        if ("auto_increment" in tgt["Extra"]) != my.autoinc:
            return False
        return True

    def session(self) -> 'MySqlSession':
        # cn = self._pool.connect()
        return MySqlSession(self._ses())


class TrState:
    def __init__(self):
        self.opand = False
        self.opor = False
        self.key = None


def _alc_build_filter(operator, key, val):
    if operator == 'gt':
        return key > val
    elif operator == 'gte':
        return key >= val
    elif operator == 'eq':
        return key == val
    elif operator == 'not':
        return key != val
    elif operator == 'lt':
        return key < val
    elif operator == 'lte':
        return key <= val
    return None


class MySqlSession(AbstractSession):

    def __init__(self, ses):
        super().__init__()
        self._ses: Session = ses
        self._res: Query = None
        self.reset()

    def close(self):
        self._ses.close()
        self._ses = None

    def reset(self) -> AbstractSession:
        self._clazz = None
        self._alcclz = None
        self._filters = []
        self._limit = 0
        self._skips = 0
        return self

    def query(self, clazz) -> AbstractSession:
        self._alcclz = ToAlc(clazz)
        self._clazz = clazz
        self._res = self._ses.query(self._alcclz)
        return self

    def bind(self, clazz) -> AbstractSession:
        return self.query(clazz)

    def filter(self, *args) -> AbstractSession:
        argc = len(args)
        if argc == 0:
            pass
        elif argc == 2:
            fp = args[0]
            rule = args[1]
            fp = _GetFieldOption(fp)
            if not fp:
                raise TypeError("filter传入的必须为store.FieldOption类型")
            fp = getattr(self._alcclz, fp.name)
            self._filters.append(rule(fp))
        elif argc == 1:
            filter = args[0]
            self._translate(filter)
        return self

    def _translate(self, f: Filter, st: TrState = None):
        if not f.key:
            if f.ands:
                st = TrState()
                st.opand = True
                for e in f.ands:
                    self._translate(e, st)
            if f.ors:
                st = TrState()
                st.opor = True
                for e in f.ors:
                    self._translate(e, st)
            if f.operator and f.value is not None:
                key = getattr(self._alcclz, st.key)
                val = f.value
                if st.opand:
                    self._filters.append(_alc_build_filter(f.operator, key, val))
                # todo OR
            return

        st = TrState()
        st.key = f.key
        if f.ands:
            st.opand = True
            for e in f.ands:
                self._translate(e, st)

    def _before(self):
        if len(self._filters):
            self._res = self._res.filter(*self._filters)
        if self._skips:
            self._res = self._res.offset(self._skips)
        if self._limit:
            self._res = self._res.limit(self._limit)

    def _after(self):
        self._filters.clear()

    def _instance(self, res: dict):
        """从原始数据恢复nnt模型"""
        t = self._clazz()
        Fill(t, res)
        # 清除修改状态
        ClearTableChangeds(t)
        return t

    def _instancealc(self, mdl):
        """从nnt模型恢复alc模型"""
        res = Output(mdl)
        t = self._alcclz()
        for k in res:
            setattr(t, k, res[k])
        return t

    def first(self):
        self._before()
        ret = None
        try:
            res = self._res.first()
            if res:
                ret = self._instance(res)
        except Exception as err:
            logger.error(err)
        self._after()
        self.reset()
        return ret

    def one(self):
        self._before()
        ret = None
        try:
            res = self._res.one()
            ret = self._instance(res)
        except Exception as err:
            logger.error(err)
        self._after()
        self.reset()
        return ret

    def add(self, m, commit=True):
        self.reset()
        self._alcclz = ToAlc(m.__class__)
        t = self._instancealc(m)
        self._ses.add(t)
        if commit:
            self.commit()
            self._ses.refresh(t)
            Fill(m, t)
        return True

    def all(self):
        ret = []
        self._before()
        try:
            cnt = self._res.count()
            if cnt >= ROWS_LIMIT:
                logger.fatal('将要读取的数量超过系统设定的最大量')
            res = self._res.all()
            for e in res:
                t = self._instance(e)
                ret.append(t)
        except Exception as err:
            logger.error(err)
        self._after()
        self.reset()
        return ret

    def limit(self, n):
        self._limit = n
        return self

    def commit(self):
        self._ses.commit()

    def count(self) -> int:
        return self._res.count()

    def skip(self, n):
        self._skips = n
        return self

    def update(self, m, commit=True) -> bool:
        cds = GetTableChangeds(m)
        if not len(cds):
            return True
        self.reset().bind(m.__class__)

        # filter主键
        prm = GetTablePrimary(m.__class__)
        if prm:
            k = getattr(self._alcclz, prm.name)
            v = getattr(m, prm.name)
            self._res = self._res.filter(k == v)
        else:
            raise TypeError("不允许更新没有主键的模型 %s" % m.__name__)

        # 更新
        sta = {}
        for e in cds:
            k = getattr(self._alcclz, e)
            v = getattr(m, e)
            sta[k] = v
        self._res.update(sta, synchronize_session=False)

        ClearTableChangeds(m)
        if commit:
            self.commit()

        return True

    def delete(self, m=None, commit=True) -> DbExecuteStat:
        self._before()
        cnt = self._res.count()
        if cnt == 0:
            self._after()
            return DbExecuteStat(remove=0)

        if m is None:
            self._res.delete()
            if commit:
                self.commit()
            self._after()
            return DbExecuteStat(remove=cnt)

        # 构造alc对象，进行删除
        t = self._instancealc(m)
        try:
            self._ses.delete(t)
            if commit:
                self.commit()
        except Exception as err:
            raise err
        finally:
            self._after()

        self._after()
        return DbExecuteStat(remove=cnt)


alc_metadata = alc.MetaData()
_alc_cache = {}


def ToAlc(clazz) -> type:
    """ 需要从nn定义的table结构转换成alc的结构 """
    ti = GetTableInfo(clazz)
    if not ti:
        return None

    fullnm = '_arc_' + clazz.__module__ + '_' + clazz.__name__
    fullnm = fullnm.replace('.', '_')
    if fullnm in _alc_cache:
        return _alc_cache[fullnm]

    # 创建一个新类
    defs = {
        '__tablename__': ti.table
    }

    # 添加字段定义
    fps = GetFieldInfos(clazz)
    for k in fps:
        fp: FieldOption = fps[k]
        cols = []
        kwcols = {}
        dc = None
        if fp.string:
            if fp.len:
                dc = alc.VARCHAR(fp.len)
            else:
                dc = alc.TEXT()
        elif fp.integer:
            dc = alc.INT()
        elif fp.double or fp.number:
            dc = alc.FLOAT()
        elif fp.boolean:
            dc = mysqltypes.TINYINT(1)
        elif fp.json or fp.array or fp.map:
            dc = alc.JSON()
        elif fp.intfloat:
            dc = alc.FLOAT()
        cols.append(dc)

        if fp.primary:
            kwcols['primary_key'] = True
        if fp.notnull:
            kwcols['nullable'] = False
        if fp.autoinc:
            kwcols['autoincrement'] = True

        defs[k] = alc.Column(*cols, **kwcols)

    clz = type(fullnm, (declarative_base(),), defs)
    _alc_cache[fullnm] = clz
    return clz
