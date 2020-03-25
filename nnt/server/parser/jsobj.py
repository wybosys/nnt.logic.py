from .parser import AbstractParser
from ...core import proto as cp
from ...core.kernel import *
from ...core.models import STATUS
from ...core.python import *


class Jsobj(AbstractParser):

    def checkInput(self, proto, params) -> int:
        fps = cp.GetAllFields(proto)
        for key in fps:
            inp = at(params, key)
            fp: cp.FieldOption = fps[key]
            if not fp.input:
                continue
            if fp.optional:
                if fp.valid and inp:
                    v = self.decodeField(fp, inp, True, False)
                    return fp.valid(v)
                continue
            if not inp:
                return STATUS.PARAMETER_NOT_MATCH
            # 判断是否合规
            if fp.valid:
                # 需要提前转换一下类型
                v = self.decodeField(fp, inp, True, False)
                return fp.valid(v)
        return STATUS.OK

    def decodeField(self, fp: cp.FieldOption, val, input: bool, output: bool):
        if fp.valtype:
            if fp.array:
                arr = []
                if val:
                    if fp.valtype == str:
                        if type(val) != list:
                            # 对于array，约定用，来分割
                            val = val.split(",")
                        if fp.valtype == cp.string_t:
                            for e in val:
                                arr.append(toString(e))
                        elif fp.valtype == cp.integer_t:
                            for e in val:
                                arr.append(toInt(e))
                        elif fp.valtype == cp.double_t:
                            for e in val:
                                arr.append(toDouble(e))
                        elif fp.valtype == cp.number_t:
                            for e in val:
                                arr.append(toNumber(e))
                        elif fp.valtype == cp.boolean_t:
                            for e in val:
                                arr.append(toBoolean(e))
                    else:
                        if type(val) == str:
                            val = toJsonObject(val)
                        if val and type(val) == list:
                            clz = fp.valtype
                            for e in val:
                                t = clz()
                                self.fill(t, e, input, output)
                                arr.append(t)
                        else:
                            logger.log("Array遇到了错误的数据 " + val)
                return arr
            elif fp.map:
                keyconv = toSelf
                if fp.keytype == cp.integer_t:
                    keyconv = toInt
                elif fp.keytype == cp.double_t:
                    keyconv = toDouble
                elif fp.keytype == cp.number_t:
                    keyconv = toNumber
                val = toJsonObject(val)
                map = {}
                if type(fp.valtype) == str:
                    if fp.valtype == cp.string_t:
                        for ek in val:
                            ev = val[ek]
                            map[keyconv(ek)] = toString(ev)
                    elif fp.valtype == cp.integer_t:
                        for ek in val:
                            ev = val[ek]
                            map[keyconv(ek)] = toInt(ev)
                    elif fp.valtype == cp.double_t:
                        for ek in val:
                            ev = val[ek]
                            map[keyconv(ek)] = toDouble(ev)
                    elif fp.valtype == cp.number_t:
                        for ek in val:
                            ev = val[ek]
                            map[keyconv(ek)] = toNumber(ev)
                    elif fp.valtype == cp.boolean_t:
                        for ek in val:
                            ev = val[ek]
                            map[keyconv(ek)] = toBoolean(ev)
                else:
                    clz = fp.valtype
                    for ek in val:
                        ev = val[ek]
                        t = clz()
                        self.fill(t, ev, input, output)
                        map[keyconv(ek)] = t
                return map
            elif fp.multimap:
                keyconv = toSelf
                if fp.keytype == cp.integer_t:
                    keyconv = toInt
                elif fp.keytype == cp.double_t:
                    keyconv = toDouble
                elif fp.keytype == cp.number_t:
                    keyconv = toNumber
                val = toJsonObject(val)
                mmap = Multimap()
                if type(fp.valtype) == str:
                    if fp.valtype == cp.string_t:
                        for ek in val:
                            ev = val[ek]
                            mmap.set(keyconv(ek), [toString(e) for e in ev])
                    elif fp.valtype == cp.integer_t:
                        for ek in val:
                            ev = val[ek]
                            mmap.set(keyconv(ek), [toInt(e) for e in ev])
                    elif fp.valtype == cp.double_t:
                        for ek in val:
                            ev = val[ek]
                            mmap.set(keyconv(ek), [toDouble(e) for e in ev])
                    elif fp.valtype == cp.number_t:
                        for ek in val:
                            ev = val[ek]
                            mmap.set(keyconv(ek), [toNumber(e) for e in ev])
                    elif fp.valtype == cp.boolean_t:
                        for ek in val:
                            ev = val[ek]
                            mmap.set(keyconv(ek), [toBoolean(e) for e in ev])
                else:
                    clz = fp.valtype
                    for ek in val:
                        ev = val[ek]
                        res = []
                        for e in ev:
                            t = clz()
                            self.fill(t, e, input, output)
                            res.append(t)
                        mmap.set(keyconv(ek), res)
                return mmap
            elif fp.enum:
                return toInt(val)
            else:
                if type(fp.valtype) != str:
                    val = toJsonObject(val)
                if fp.valtype == object:
                    return val
                clz = fp.valtype
                t = clz()
                self.fill(t, val, input, output)
                return t
        else:
            if fp.string:
                return toString(val)
            elif fp.integer:
                return toInt(val)
            elif fp.double:
                return toDouble(val)
            elif fp.number:
                return toNumber(val)
            elif fp.intfloat:
                return IntFloat(toInt(val), fp.intfloat)
            elif fp.boolean:
                return toBoolean(val)
            elif fp.enum:
                return toInt(val)
            elif fp.json:
                return toJsonObject(val)
            elif fp.file:
                if type(val) == str:
                    return val
                return UploadedFileHandle(val)
            elif fp.filter:
                return Filter.Parse(val)
            else:
                return val

    def fill(self, mdl, params, input: bool, output: bool):
        fps = cp.GetAllFields(mdl)
        for key in params:
            fp: cp.FieldOption = at(fps, key)
            if fp == None:
                continue
            if input and not fp.input:
                continue
            if output and not fp.output:
                continue
            mdl[key] = self.decodeField(fp, params[key], input, output)
