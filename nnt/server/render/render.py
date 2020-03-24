from ...core import logger
from ..transaction import *


class AbstractRender:

    def __init__(self):
        super().__init__()

        # 输出的类型
        self.type: str = None

    def render(self, trans: Transaction, opt: TransactionSubmitOption = None) -> str:
        """渲染数据"""
        pass


_renders: [str, AbstractRender] = {}


def RegisterRender(name: str, render: AbstractRender):
    """ 注册渲染组件 """
    if name in _renders:
        logger.fatal("重复注册渲染器" + name)
        return
    _renders[name] = render


def FindRender(name: str) -> AbstractRender:
    if name in _renders:
        return _renders[name]
    return _renders['json']
