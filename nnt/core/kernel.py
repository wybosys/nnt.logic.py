import json
import asyncio
from . import logger


def toJson(o, default=None):
    r = None
    try:
        r = json.dumps(o)
    except:
        r = default
    return r


def toJsonObject(o, default=None):
    t = type(o)
    if t == string:
        if o == "undefined" or o == "null":
            return default
        r = None
        try:
            r = json.loads(o)
        except Exception as err:
            logger.warn(o + " " + err)
            r = default
        return r
    elif t == dict or t == list:
        return o
    return default


def corun(func):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())
    loop.close()

def toSelf(obj):
    return obj

def toString(obj):
    return str(obj)

def toInt(obj):
    return int(obj)

def toDouble(obj):
    return float(obj)

def toNumber(obj):
    return float(obj)

def toBoolean(obj):
    return not not obj