import asyncio
import json
import uuid as muuid

from . import logger


def uuid() -> str:
    return muuid.uuid1().hex


def toJson(o, default=None):
    r = None
    try:
        r = json.dumps(o)
    except:
        r = default
    return r


def toJsonObject(o, default=None):
    t = type(o)
    if t == str:
        if o == "undefined" or o == "null":
            return default
        r = None
        try:
            r = json.loads(o)
        except Exception as err:
            logger.warn(o)
            logger.error(err)
            r = default
        return r
    elif t == dict or t == list:
        return o
    return default


def corun(func):
    loop = asyncio.get_event_loop()
    if callable(func):
        loop.run_until_complete(func())
    else:
        loop.run_until_complete(func)
    loop.close()


def toSelf(obj):
    return obj


def toString(obj, default=''):
    if obj is None:
        return default
    typ = type(obj)
    if typ == list or typ == map:
        return toJson(typ, default)
    return str(obj)


def toInt(obj, default=0):
    try:
        return int(obj)
    except:
        return default


def toDouble(obj, default=0):
    try:
        return float(obj)
    except:
        return default


def toNumber(obj, default=0):
    if obj is None:
        return default
    if type(obj) == str:
        return toDouble(obj, default) if '.' in obj else toInt(obj, default)
    try:
        return float(obj)
    except:
        return default


def toBoolean(obj):
    if obj is None:
        return False
    if obj == "true":
        return True
    if obj == "false":
        return False
    return not not obj


def toObject(obj):
    return obj


class IntFloat:
    """ 用int来表示float """

    def __init__(self, ori: int = 0, s: int = 1):
        super().__init__()

        self._ori = ori
        self._s = s
        self._value = ori / s

    @staticmethod
    def Money(ori: int = 0) -> 'IntFloat':
        return IntFloat(ori, 100)

    @staticmethod
    def Percentage(ori: int = 0) -> 'IntFloat':
        return IntFloat(ori, 10000)

    @staticmethod
    def Origin(ori):
        if isinstance(ori, IntFloat):
            return ori.origin
        raise TypeError('对一个不是IntFloat的数据请求Origin')

    @staticmethod
    def Unserilize(ori) -> 'IntFloat':
        return IntFloat(ori['_ori'], ori['_s'])

    @staticmethod
    def From(ori, scale: int) -> 'IntFloat':
        if isinstance(ori, IntFloat):
            return IntFloat(ori.origin, scale)
        return IntFloat(ori, scale)

    @staticmethod
    def FromValue(val, scale: int) -> 'IntFloat':
        if isinstance(val, IntFloat):
            return IntFloat(val.origin, scale)
        return IntFloat(0, scale).setValue(val)

    @staticmethod
    def Multiply(l, r: int) -> 'IntFloat':
        if isinstance(l, IntFloat):
            return l.clone().multiply(r)
        raise TypeError('对一个不是IntFloat的数据进行multiply操作')

    @staticmethod
    def Add(l, r: int) -> 'IntFloat':
        if isinstance(l, IntFloat):
            return l.clone().add(r)
        raise TypeError('对一个不是IntFloat的数据进行multiply操作')

    def valueOf(self):
        return self._value

    def toString(self) -> str:
        return str(self._value)

    @property
    def value(self):
        """ 缩放后的数据，代表真实值 """
        return this._value

    @value.setter
    def value(self, v):
        self._value = v
        self._ori = int(v * self._s)

    def setValue(self, v) -> 'IntFloat':
        self.value = v
        return self

    @property
    def origin(self):
        """ 缩放前的数据 """
        return self._ori

    @origin.setter
    def origin(self, ori):
        self._ori = int(ori)
        self._value = ori / self._s

    @property
    def scale(self):
        return self._s

    def toNumber(self):
        return self.value

    def toDouble(self):
        return self.value

    def toInt(self):
        return int(self.value)

    def toBoolean(self):
        return self.value != 0

    def add(self, r) -> 'IntFloat':
        self.value += r
        return self

    def multiply(self, r) -> 'IntFloat':
        self.value *= r
        return self

    def clone(self) -> 'IntFloat':
        return IntFloat(self._ori, self._s)

    def __copy__(self):
        return self.clone()
