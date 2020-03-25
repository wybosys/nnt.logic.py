import inspect

# 定义标记
input = 0
output = 1
optional = 2
hidden = 3
auth = 4
enum = 5
constant = 6
required = 7

# 定义类型
string_t = str
integer_t = int
double_t = float
boolean_t = bool


class number_t: pass


class ModelOption:

    def __init__(self):
        super().__init__()

        # 需要登陆验证
        self.auth = False

        # 是否是枚举类型，因为语言限制，无法对enum对象添加decorate处理，只能在服务器端使用class来模拟
        self.enum = False

        # 用来定义常量，或者模拟str的枚举
        self.constant = False

        # 隐藏后就不会加入到models列表中
        self.hidden = False

        # 父类，目前用来生成api里面的父类名称
        self.parent = None


class FieldValidProc:

    def __init__(self):
        super().__init__()

        # 可以附加一个错误码
        self.status = None

        # 当返回false时，即为验证失败，此时上层可以通过获取status来返回特定的错误状态码
        self.fn = None  # (inp: any): boolean


class FieldOption:

    def __init__(self):
        super().__init__()

        # 唯一序号，后续类似pb的协议会使用id来做数据版本兼容
        self.id: int = 0

        # 可选
        self.optional: bool = False

        # 读取控制
        self.input: bool = False
        self.output: bool = False

        # 类型标签
        self.array: bool = False
        self.map: bool = False
        self.multimap: bool = False
        self.string: bool = False
        self.integer: bool = False
        self.double: bool = False
        self.number: bool = False
        self.boolean: bool = False
        self.enum: bool = False
        self.file: bool = False
        self.json: bool = False
        self.filter: bool = False
        self.intfloat: int = None

        # 关联类型
        self.keytype = None
        self.valtype = None

        # 注释
        self.comment = None

        # 有效性检查函数, FieldValidProc 或者 函数
        self.valid = None
        self.valid_result: int = None


MP_KEY = "__modelproto"


def model(options=None, parent=None):
    def _(clazz):
        mp = ModelOption()
        if options:
            mp.auth = auth in options
            mp.enum = enum in options
            mp.constant = constant in options
            mp.hidden = hidden in options
        mp.parent = parent
        setattr(clazz, MP_KEY, mp)
        return clazz

    return _


def field(id, options, comment, valid) -> FieldOption:
    r = FieldOption()
    r.id = id
    if options:
        r.input = input in options
        r.output = output in options
        r.optional = optional in options
    r.comment = comment
    r.valid = valid
    return r


def string(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.string = True
    return fp


def boolean(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.boolean = True
    return fp


def integer(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.integer = True
    return fp


def double(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.double = True
    return fp


def number(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.number = True
    return fp


def intfloat(id, scale, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.intfloat = scale
    return fp


def percentage(id, opts=None, comt=None, valid=None):
    """ 百分数格式化至 0-10000之间 """
    return intfloat(id, 10000, opts, comt, valid)


def money(id, opts=None, comt=None, valid=None):
    """ 钱,格式化到 0-100 之间 """
    return intfloat(id, 100, opts, comt, valid)


def array(id, typ, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.array = True
    fp.valtype = typ
    return fp


def map(id, keytyp, valtyp, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.map = True
    fp.keytype = keytyp
    fp.valtype = keytyp
    return fp


def json(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.json = True
    return fp


def typer(id, typ, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.valtype = typ
    return fp


def enumerate(id, clazz, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.enum = True
    fp.valtype = clazz
    return fp


def file(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.file = True
    return fp


def filter(id, opts=None, comt=None, valid=None):
    fp = field(id, opts, comt, valid)
    fp.filter = True
    return fp


def GetModelInfo(clz) -> ModelOption:
    if hasattr(clz, MP_KEY):
        return clz[MP_KEY]
    return None


def IsModel(clz) -> bool:
    """ 是否是模型 """
    return GetModelInfo(clz) != None


def IsNeedAuth(mdl) -> bool:
    """ 是否需要登陆验证 """
    mp = GetModelInfo(mdl.__class__)
    return mp.auth


def GetAllFields(clazz) -> [str, FieldOption]:
    fs = {}
    for e in inspect.getmembers(clazz):
        nm = e[0]
        obj = e[1]
        if isinstance(obj, FieldOption):
            fs[nm] = obj
    return fs
