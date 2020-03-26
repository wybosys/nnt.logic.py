from inspect import *


def notroutine(obj):
    return not isroutine(obj)


def getmemberfields(obj):
    arr = []
    for e in getmembers(obj, notroutine):
        nm, obj = e
        if nm.startswith('_'):
            continue
        arr.append(e)
    return arr
