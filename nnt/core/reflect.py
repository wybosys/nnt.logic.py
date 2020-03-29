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
    for each in getmemberfields(obj):
        if ismemberfield(each[1]):
            setattr(obj, each[0], None)
    # 调用对象自身初始化
    obj.__init__(*args, **kwargs)
    return obj


def getmemberfields(obj):
    arr = []
    if type(obj) != type:
        # 不是类对象，转换成类，因memberfield只对类定义有意义
        obj = obj.__class__
    names = dir(obj)
    for name in names:
        if name.startswith('_'):
            continue
        v = getattr(obj, name)
        if ismemberfield(v):
            arr.append((name, v))
    return arr
