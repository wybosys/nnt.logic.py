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
