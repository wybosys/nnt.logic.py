from nnt.store.proto import FieldOption
from nnt.store.store import AbstractDbms


class AbstractRdb(AbstractDbms):

    def compareFieldDef(self, my: FieldOption, tgt) -> bool:
        """比较字段定义和手写定义是否有变化"""
        pass


def FpToRelvDefType(fp: FieldOption) -> str:
    if fp.string:
        return "char(128)" if fp.key else "text"
    if fp.integer:
        return "int"
    if fp.double:
        return "double"
    if fp.boolean:
        return "tinyint(1)"
    if fp.json:
        return "json"
    return "json"  # 默认的是json数据，这样既可以吃掉大部分数据结构
