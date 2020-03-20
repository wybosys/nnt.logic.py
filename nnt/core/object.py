from ..core.kernel import *


class ISerializableObject:

    def serialize(self):
        """ 序列化 """
        return ''

    def unserialize(self, str):
        """ 反序列化 """
        return False


class VariantType:
    UNKNOWN = 0
    BUFFER = 1
    STRING = 2
    OBJECT = 3
    BOOLEAN = 4
    NUMBER = 5


class Variant(ISerializableObject):

    def __init__(self, o=None):
        super().__init__()

        self._raw = None
        self._type = VariantType.UNKNOWN

        self._buf = None
        self._str = None
        self._bol = None
        self._num = None
        self._obj = None

        self._raw = o
        if not o:
            return

        typ = type(o)
        if typ == bytearray:
            self._type = VariantType.BUFFER
            self._buf = o
        elif typ == string:
            self._type = VariantType.STRING
            self._str = o
        elif typ == bool:
            self._type = VariantType.BOOLEAN
            self._bol = o
        elif typ == int or typ == float:
            self._type = VariantType.NUMBER
            self._num = o
        else:
            self._type = VariantType.OBJECT
            self._obj = o

    @property
    def typ(self):
        return self._type

    @property
    def raw(self):
        return self._raw

    @staticmethod
    def Unserialize(str):
        if not str:
            return None
        t = Variant()
        if not t.unserialize(str):
            return None
        return t

    @property
    def number(self):
        return self._num

    @property
    def object(self):
        return self._obj

    @property
    def value(self):
        if self._type == VariantType.STRING:
            return self._str
        elif self._type == VariantType.BUFFER:
            return self._buf
        elif self._type == VariantType.OBJECT:
            return self._obj
        elif self._type == VariantType.BOOLEAN:
            return self._bol
        elif self._type == VariantType.NUMBER:
            return self._num
        return None

    @value.setter
    def value(self, v):
        if self._type == VariantType.STRING:
            self._str = v
        elif self._type == VariantType.BUFFER:
            self._buf = v
        elif self._type == VariantType.OBJECT:
            self._obj = v
        elif self._type == VariantType.BOOLEAN:
            self._bol = v
        elif self._type == VariantType.NUMBER:
            self._num = v

    @property
    def buffer(self):
        if self._buf:
            return self._buf
        self._buf = self.string.encode('utf-8')
        return self._buf

    @property
    def string(self):
        if self._str:
            return self._str
        if self._type == VariantType.BUFFER:
            self._str = self._buf.decode('utf-8')
        elif self._type == VariantType.OBJECT:
            self._str = toJson(self._obj)
        elif self._type == VariantType.BOOLEAN:
            self._str = 'true' if self._bol else 'false'
        elif self._type == VariantType.NUMBER:
            self._str = str(self._num)
        return self._str

    @property
    def object(self):
        if self._obj:
            return self._obj
        self._obj = toJsonObject(self.string)
        return self._jsobj

    def serialize(self):
        s = {
            't': self._type,
            '_i': 'vo',
            '_d': self.value
        }
        return toJson(s)

    def unserialize(self, str):
        obj = toJsonObject(str)
        if not obj:
            return False
        if obj._i != "vo":
            typ = type(obj)
            if typ == int or typ == float:
                self._type = VariantType.NUMBER
                self._num = obj
                return True
            elif typ == string:
                self._type = VariantType.STRING
                self._str = obj
                return True
            elif typ == bool:
                self._type = VariantType.BOOLEAN
                self._bol = obj
                return True
            return False
        self._type = obj._t
        self.value = obj._d
        return True
