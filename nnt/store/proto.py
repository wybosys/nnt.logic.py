key = 0
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

        self.key = False  # 主键
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


def column(opts=None, setting=None) -> FieldOption:
    """返回基础的定义结构，之后的都直接使用固定的类型函数来声明"""
    fp = FieldOption()
    if opts:
        fp.key = key in opts
        fp.subkey = subkey in opts
        fp.notnull = notnull in opts
        fp.autoinc = autoinc in opts
        fp.unique = unique in opts
        fp.unsign = unsign in opts
        fp.zero = zero in opts
        fp.desc = desc in opts
        fp.loose = loose in opts
    fp.setting = setting
    return fp


def string(opts=None, setting=None):
    fp = column(opts)
    fp.string = True
    return fp


def boolean(opts=None, setting=None):
    fp = column(opts)
    fp.boolean = True
    return fp


def integer(opts=None, setting=None):
    fp = column(opts)
    fp.integer = True
    return fp


def double(opts=None, setting=None):
    fp = column(opts)
    fp.double = True
    return fp


def number(opts=None, setting=None):
    fp = column(opts)
    fp.number = True
    return fp


def intfloat(scale, opts=None, setting=None):
    fp = column(opts)
    fp.intfloat = scale
    return fp


def percentage(opts=None, setting=None):
    return intfloat(10000, opts, setting)


def money(opts=None, setting=None):
    return intfloat(100, opts, setting)


def array(typ, opts=None, setting=None):
    fp = column(opts)
    fp.array = True
    fp.valtype = typ
    return fp


def map(keytyp, valtyp, opts=None, setting=None):
    fp = column(opts)
    fp.map = True
    fp.keytype = keytyp
    fp.valtype = valtyp
    return fp


def json(opts=None, setting=None):
    fp = column(opts)
    fp.json = True
    return fp


def typer(typ, opts=None, setting=None):
    fp = column(opts)
    fp.valtype = typ
    return fp
