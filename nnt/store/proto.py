import inspect

from nnt.core.kernel import toSelf, toInt, toDouble, IntFloat, toObject, toString, toNumber
from nnt.core.proto import integer_t, double_t
from nnt.core.python import *

key = primary = 0
subkey = 1
notnull = 2
autoinc = 3
unique = 4
unsign = 5
zero = 6
desc = 7
strict = 0x20  # 默认：严格模式，以数据库中的数据为准
loose = 0x21  # 宽松模式，以传入的model对象为准

MP_KEY = "__dbproto"
INNERID_KEY = "__innerid"


class TableSetting:

    def __init__(self):
        super().__init__()

        # 生命期
        self.ttl: float = None


class FieldSetting:

    def __init__(self):
        super().__init__()

        # 生命期
        self.ttl: float = None


class TableInfo:

    def __init__(self):
        super().__init__()

        # 数据库连接名
        self.id: str = None

        # 数据表名
        self.table: str = None

        # 设置
        self.setting: TableSetting = None


class FieldOption:

    def __init__(self):
        super().__init__()

        self.name: str = None
        self.string = False
        self.integer = False
        self.double = False
        self.number = False
        self.boolean = False
        self.json = False
        self.array = False
        self.map = False
        self.intfloat = None

        self.keytype = None
        self.valtype = None

        self.primary = False  # 主键
        self.subkey = False  # 次键
        self.notnull = False  # 不能为空
        self.autoinc = False  # 自增
        self.unique = False  # 不重复
        self.unsign = False  # 无符号
        self.zero = False  # 初始化为0
        self.desc = False  # 递减
        self.loose = False  # 宽松模式
        self.scale = None  # 数据缩放

        self.setting: FieldSetting = None  # 字段设置
        self.len: int = None  # 数据长度


def FpIsTypeEqual(l: FieldOption, r: FieldOption) -> bool:
    return l.string == r.string and \
           l.integer == r.integer and \
           l.double == r.double and \
           l.boolean == r.boolean and \
           l.number == r.number and \
           l.intfloat == r.intfloat and \
           l.json == r.json and \
           l.array == r.array and \
           l.map == r.map and \
           l.keytype == r.keytype and \
           l.valtype == r.valtype and \
           l.loose == r.loose


def table(dbid: str, tbnm: str, setting: TableSetting = None):
    """定义一个数据表模型，注意：数据表模型不能继承"""

    def _(clazz):
        dp = TableInfo()
        dp.id = dbid
        dp.table = tbnm
        dp.setting = setting
        setattr(clazz, MP_KEY, dp)
        return clazz

    return _


def GetStoreInfo(clazz) -> TableInfo:
    if hasattr(clazz, MP_KEY):
        return getattr(clazz, MP_KEY)
    return None


def _IsFieldOption(obj) -> bool:
    typ = type(obj)
    if typ == tuple or typ == list:
        for e in obj:
            if isinstance(e, FieldOption):
                return True
    else:
        return isinstance(obj, FieldOption)


def _GetFieldOption(v) -> FieldOption:
    typ = type(v)
    if typ == list or typ == tuple:
        for e in v:
            if isinstance(e, FieldOption):
                return e
    elif isinstance(v, FieldOption):
        return v
    return None


def GetFieldInfos(clazz) -> [str, FieldOption]:
    fs = {}
    for e in inspect.getmembers(clazz):
        nm, obj = e
        obj = _GetFieldOption(obj)
        if obj:
            fs[nm] = obj
            if obj.name is None:
                obj.name = nm
    return fs


def column(opts=None, setting=None) -> FieldOption:
    """返回基础的定义结构，之后的都直接使用固定的类型函数来声明"""
    fp = FieldOption()
    if opts:
        fp.primary = key in opts
        fp.subkey = subkey in opts
        fp.notnull = notnull in opts
        fp.autoinc = autoinc in opts
        fp.unique = unique in opts
        fp.unsign = unsign in opts
        fp.zero = zero in opts
        fp.desc = desc in opts
        fp.loose = loose in opts
    return fp


def string(opts=None, setting=None, len=0):
    fp = column(opts, setting)
    fp.string = True
    fp.len = len
    return fp


def boolean(opts=None, setting=None):
    fp = column(opts, setting)
    fp.boolean = True
    return fp


def integer(opts=None, setting=None):
    fp = column(opts, setting)
    fp.integer = True
    return fp


def double(opts=None, setting=None):
    fp = column(opts, setting)
    fp.double = True
    return fp


def number(opts=None, setting=None):
    fp = column(opts, setting)
    fp.number = True
    return fp


def intfloat(scale, opts=None, setting=None):
    fp = column(opts, setting)
    fp.intfloat = scale
    return fp


def percentage(opts=None, setting=None):
    return intfloat(10000, opts, setting)


def money(opts=None, setting=None):
    return intfloat(100, opts, setting)


def array(typ, opts=None, setting=None):
    fp = column(opts, setting)
    fp.array = True
    fp.valtype = typ
    return fp


def map(keytyp, valtyp, opts=None, setting=None):
    fp = column(opts, setting)
    fp.map = True
    fp.keytype = keytyp
    fp.valtype = valtyp
    return fp


def json(opts=None, setting=None):
    fp = column(opts, setting)
    fp.json = True
    return fp


def typer(typ, opts=None, setting=None):
    fp = column(opts, setting)
    fp.valtype = typ
    return fp


def Fill(mdl, params: dict) -> object:
    """ 填数据库对象 """
    fps = GetFieldInfos(mdl.__class__)
    if not fps:
        return mdl
    for key in fps:
        fp: FieldOption = fps[key]
        val = at(params, key)
        if not val:
            c = getattr(mdl, key)
            if isinstance(c, FieldOption):
                setattr(mdl, key, None)
            continue
        if fp.valtype:
            if fp.array:
                if type(fp.valtype) == str:
                    setattr(mdl, key, val)
                else:
                    clz = fp.valtype
                    if clz == object:
                        # object类似于json，不指定数据类型
                        setattr(mdl, key, val)
                    else:
                        arr = []
                        for e in val:
                            t = clz()
                            Decode(t, e)
                            arr.append(t)
                        setattr(mdl, key, arr)
            elif fp.map:
                m = {}

                # 根据申明的类型，构造不同的map
                keyconv = toSelf
                if fp.keytype == integer_t:
                    keyconv = toInt
                elif fp.keytype == double_t:
                    keyconv = toDouble

                if type(fp.valtype) == str:
                    for ek in val:
                        m[keyconv(ek)] = val[ek]
                else:
                    clz = fp.valtype
                    for ek in val:
                        t = clz()
                        Decode(t, val[ek])
                        m[keyconv(ek)] = t
                setattr(mdl, key, m)
            else:
                clz = fp.valtype;
                if clz == object:
                    setattr(mdl, key, val)
                elif type(val) == dict:
                    t = clz()
                    Decode(t, val)
                    setattr(mdl, key, t)
                elif not fp.loose:
                    setattr(mdl, key, None)
        elif fp.intfloat:
            v = IntFloat.From(val, fp.intfloat)
            setattr(mdl, key, v)
        else:
            setattr(mdl, key, val)
    return mdl;


def Decode(mdl, params: dict) -> object:
    """ 填数据库对象 """
    fps = GetFieldInfos(mdl.__class__)
    if fps is None:
        return mdl
    for key in params:
        fp: FieldOption = at(fps, key)
        if fp is None:
            continue
        val = params[key]
        if val is None:
            if not fp.loose:
                setattr(mdl, key, None)
                # 从数据库读取数据时采用严格模式：字段如果在数据库中为null，则拿出来后也是null
            continue
        if fp.valtype:
            if fp.array:
                if type(fp.valtype) == str:
                    setattr(mdl, key, val)
                else:
                    clz = fp.valtype
                    if clz == object:
                        # object类似于json，不指定数据类型
                        setattr(mdl, key, val)
                    else:
                        arr = []
                        for e in val:
                            t = clz()
                            Decode(t, e)
                            arr.append(t)
                        setattr(mdl, key, arr)
            elif fp.map:
                m = {}

                # 根据申明的类型，构造不同的map
                keyconv = toSelf
                if fp.keytype == integer_t:
                    keyconv = toInt
                elif fp.keytype == double_t:
                    keyconv = toDouble

                if type(fp.valtype) == str:
                    for ek in val:
                        m[keyconv(ek)] = val[ek]
                else:
                    clz = fp.valtype
                    for ek in val:
                        t = clz()
                        Decode(t, val[ek])
                        m[keyconv(ek)] = t
                setattr(mdl, key, m)
            else:
                clz = fp.valtype;
                if clz == object:
                    setattr(mdl, key, val)
                elif type(val) == dict:
                    t = clz()
                    Decode(t, val)
                    setattr(mdl, key, t)
                elif not fp.loose:
                    setattr(mdl, key, None)
        elif fp.intfloat:
            v = IntFloat.From(val, fp.intfloat)
            setattr(mdl, key, v)
        else:
            setattr(mdl, key, val)
    return mdl;


def Output(mdl, default: dict = {}) -> dict:
    if not mdl:
        return default
    fps = GetFieldInfos(mdl.__class__)
    if not fps:
        return default
    r = {}
    for fk in fps:
        fp: FieldOption = fps[fk]
        if not hasattr(mdl, fk):
            continue
        val = getattr(mdl, fk)
        if isinstance(val, FieldOption):
            val = None
        if fp.valtype:
            if fp.array:
                if type(fp.valtype) == str:
                    r[fk] = val;
                else:
                    arr = []
                    if val:
                        for e in val:
                            arr.append(Output(e))
                    r[fk] = arr
            elif fp.map:
                m = {}
                if val:
                    if type(fp.valtype) == str:
                        for k in val:
                            m[k] = val[k]
                    else:
                        for k in val:
                            m[k] = Output(val[k])
                r[fk] = m
            else:
                v = Output(val, None)
                if v is None:
                    v = toObject(val)
                r[fk] = v;
        elif fp.intfloat:
            r[fk] = IntFloat.From(val, fp.intfloat).origin
        elif fp.string:
            r[fk] = toString(val)
        elif fp.number:
            r[fk] = toNumber(val);
        elif fp.integer:
            if not fp.autoinc:
                r[fk] = toInt(val)
        elif fp.double:
            r[fk] = toDouble(val)
        else:
            r[fk] = val
    return r
