# -*- coding:utf-8 -*-

import json
from . import logger

def toJson(o, default = None):
    r = None
    try:
        r = json.dumps(o)
    except:
        r = default    
    return r

def toJsonObject(o, default = None):
    t = type (o)
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
