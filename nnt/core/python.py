import os


# 扩展python基础函数


def indexOf(lst, v):
    return lst.index(v) if v in lst else -1


def at(any, idx, default=None):
    try:
        return any[idx]
    except:
        try:
            return getattr(any, idx)
        except:
            return default


def ats(any, *args, default=None):
    t = at(any, args[0], None)
    if not t:
        return ats(any, args[1:], default)
    return default


def atpath(any, path: str, default=None):
    return ats(any, *path.split('.'), default)


def delete(any, idx):
    try:
        del any[idx]
    except:
        pass


def nonnull1st(*args):
    for e in args:
        if e != None:
            return e
    return None


def get_file_content(file):
    if not os.path.exists(file):
        return ''
    return ''.join(open(file).readlines())


def obj_get_classname(obj, default=None) -> str:
    try:
        typ = type(obj)
        if typ == str:
            return obj
        if typ == type:
            return obj.__name__
        return obj.__class__.__name__
    except:
        return default


def obj_get_class(obj, default=None):
    typ = type(obj)
    if typ == type:
        return obj
    return typ


POD_TYPES = [str, int, float, bool]


def type_ispod(typ) -> bool:
    return typ in POD_TYPES


class StringT:

    @staticmethod
    def Split(s: str, sep: str, skipempty: bool = True) -> [str]:
        """ 拆分，可以选择是否去空 """
        r = s.split(sep)
        r0 = []
        for e in r:
            if e or not skipempty:
                r0.append(e)
        return r0


class multimap:

    def __init__(self):
        self._m = {}

    def set(self, k, arr):
        if type(arr) != list:
            raise TypeError("multimap的set只接受list类型")
        self._m[k] = arr

    def __len__(self):
        return self._m.__len__()

    def __getitem__(self, item):
        return self._m.__getitem__(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __iter__(self):
        return self._m.__iter__()

    def clear(self):
        self._m.clear()
