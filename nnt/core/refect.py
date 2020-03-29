from . import inspect


# 数据描述字段类
class memberfield:
    pass


def ismemberfield(obj) -> bool:
    if isinstance(obj, memberfield):
        return True
    typ = type(obj)
    if typ == list or typ == tuple:
        for e in obj:
            if isinstance(e, memberfield):
                return True
    return False


def __hook_new__(cls, *args, **kwargs):
    old = getattr(cls, '__create__')
    obj = old(cls)
    # 初始化fp为None
    for each in inspect.getmemberfields(obj):
        if ismemberfield(each[1]):
            setattr(obj, each[0], None)
    # 调用对象自身初始化
    obj.__init__(*args, **kwargs)
    return obj
