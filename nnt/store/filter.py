from ..core.python import *

# 基于json定义用来解析

"""
{
    "and": [
         "abc": { "gt": 100 }
         ]
}
"""
from nnt.core import kernel, logger

KEYWORDS = ["and", "or"]
OPERATORS = ["gt", "gte", "eq", "not", "lt", "lte"]


class Filter:

    def __init__(self):
        self.ands: list['Filter'] = []
        self.ors: list['Filter'] = []
        self.key: str = None
        self.operator: str = None
        self.value: object = None

    def clear(self):
        self.ands.clear()
        self.ors.clear()
        self.key = None

    def __str__(self):
        r = {}
        self._attachToJson(r)
        return kernel.toJson(r)

    def parse(self, jsobj: dict) -> bool:
        """ 解析，如果解析全新，需要手动调用clear方法 """
        for k in jsobj:
            v = jsobj[k]

            if k == "and":
                if type(v) == list:
                    for e in v:
                        sub = Filter()
                        if sub.parse(e):
                            self.ands.append(sub)
                        else:
                            logger.error("filter解析失败 %s" % kernel.toJson(e))
                            return False
                else:
                    logger.error('filter解析失败 %s' % kernel.toJson(v))
                    return False
            elif k == 'or':
                if type(v) == list:
                    for e in v:
                        sub = Filter()
                        if sub.parse(e):
                            self.ors.append(sub)
                        else:
                            logger.error('filter解析失败 %s' % kernel.toJson(v))
                            return False
                else:
                    logger.error('filter解析失败 %s' % kernel.toJson(v))
                    return False
            elif k in OPERATORS:
                self.operator = k
                self.value = v
            else:
                self.key = k
                if type_ispod(type(v)):
                    return False
                for sk in v:
                    sv = v[sk]
                    sub = Filter()
                    sub.operator = sk
                    sub.value = sv
                    self.ands.append(sub)
        return True

    @staticmethod
    def Parse(str: str, default=None) -> 'Filter':
        jsobj = kernel.toJsonObject(str)
        if not jsobj:
            return default
        r = Filter()
        if not r.parse(jsobj):
            return default
        return r

    def _attachToJsobj(self, obj: dict):
        if self.key is None:
            if len(self.ands):
                if 'and' not in obj:
                    obj['and'] = []
                for e in self.ands:
                    ref = {}
                    obj['and'].push(ref)

                    e._attachToJsobj(ref)

            if len(self.ors):
                if 'or' not in obj:
                    obj['or'] = []
                for e in self.ors:
                    ref = {}
                    obj['or'].push(ref)

                    e._attachToJsobj(ref)

            if self.operator is not None and self.value is not None:
                obj[self.operator] = self.value

        if self.key:
            # 生成新的子节点
            ref = {}
            obj[self.key] = ref

            if len(self.ands):
                if 'and' not in ref:
                    ref['and'] = []
                for e in self.ands:
                    t = {}
                    ref['and'].push(t)

                    e._attachToJsobj(t)

            if len(self.ors):
                if 'or' not in ref:
                    ref['or'] = []
                for e in self.ors:
                    t = {}
                    ref['or'].push(t)

                    e._attachToJsobj(t)
