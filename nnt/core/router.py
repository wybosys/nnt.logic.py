from ..manager import config
import sys


class IRouter:

    def __init__(self):
        super().__init__()

        # router的标记
        self.action = None

    def config(self, cfg) -> bool:
        """ 接受配置文件的设置 """
        return True


# action可用的模式
debug = 'debug'
develop = 'develop'
local = 'local'
expose = 'expose'
devops = 'devops'
devopsdevelop = 'devopsdevelop'
devopsrelease = 'devopsrelease'

# 打开频控
frqctl = 'frqctl'


class ActionProto:

    def __init__(self):
        super().__init__()
        self._custom = {}

        # 绑定的模型类型
        self.clazz = None

        # 限制debug可用
        self.debug = False

        # 限制develop可用
        self.develop = False

        # 限制local可用
        self.local = False

        # 限制devops可用
        self.devops = False

        # 限制devopsdevelop可用
        self.devopsdevelop = False

        # 限制devopsrelease可用
        self.devopsrelease = False

        # 注释
        self.comment = None

        # 打开频控
        self.frqctl = False

        # 暴露接口
        self.expose = False


# 基于python的包装器的特性，函数包装执行时类对象并没有声明，所以之能采用全局映射函数数据组到类名上
_actions = {}


def action(mdlclz, options=None, comment=None):
    """ 定义router需要的model对象 """
    def _(fun):
        ap = ActionProto()
        ap.clazz = mdlclz
        ap.comment = comment

        # 判断action是否在当前环境下开放
        pas = True
        if options:
            for e in options:
                setattr(ap, e, True)

            # options默认为空代表开放，其他情形检测环境参数
            optcheck = debug in options or develop in options or local in options or devops in options or devopsdevelop in options or devopsrelease in options

            # 检测环境
            if optcheck:
                pas = False
                if not pas and ap.debug and config.DEBUG:
                    pas = True
                if not pas and ap.develop and config.DEVELOP:
                    pas = True
                if not pas and ap.local and config.LOCAL:
                    pas = True
                if not pas and ap.devops and config.DEVOPS:
                    pas = True
                if not pas and ap.devopsdevelop and config.DEVOPS_DEVELOP:
                    pas = True
                if not pas and ap.devopsrelease and config.DEVOPS_RELEASE:
                    pas = True

        if pas:
            # 获得action对应的router类
            clazznm = fun.__qualname__.partition('.')[0]
            modunm = fun.__module__
            clazzpath = modunm + '.' + clazznm
            if clazzpath not in _actions:
                _actions[clazzpath] = {}
            _actions[clazzpath][fun.__name__] = ap
        return fun
    return _


def FindAction(target, key: str) -> ActionProto:
    clazz = target.__class__
    modunm = clazz.__module__
    clazzpath = modunm + '.' + clazz.__name__
    if clazzpath not in _actions:
        return None
    return _actions[clazzpath][key]


def GetAllActionNames(target) -> [str]:
    clazz = target.__class__
    modunm = clazz.__module__
    clazzpath = modunm + '.' + clazz.__name__
    if clazzpath not in _actions:
        return None
    return list(_actions[clazzpath].keys())
