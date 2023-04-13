from ...core import proto as cp, logger, models


class AbstractParser:
    """Paser负责将不同协议传输的数据回写刀模型中，根据不同的协议，params有时为json，有时是字节流"""

    def checkInput(self, proto, params) -> int:
        """检查模型和输入数据的匹配情况，返回status的错误码"""
        return models.STATUS.OK

    def decodeField(self, fp: cp.FieldOption, val, input: bool, output: bool):
        """根据属性定义解码数据"""
        pass

    def fill(self, mdl, params, input: bool, output: bool):
        """将数据从参数集写入模型"""
        pass


_parsers: dict[str, AbstractParser] = {}


def RegisterParser(name: str, parser: AbstractParser):
    if name in _parsers:
        logger.fatal("重复注册解析器" + name)
        return
    _parsers[name] = parser


def FindParser(name: str) -> AbstractParser:
    if name in _parsers:
        return _parsers[name]
    return _parsers["jsobj"]
