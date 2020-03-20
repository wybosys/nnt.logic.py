from ..manager import config

class IRouter:

    def __init__(self):
        super().__init__()

        # router的标记
        self.action = None

        # 接受配置文件的设置
        self.config = None

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

AP_KEY = "__actionproto"

# 定义router需要的model对象
def action(model, options = None, comment = None):
    ap = ActionProto()
    ap.clazz = model
    ap.comment = comment    
    if options:
        for e in options:
            setattr(ap, e, True)
    # 判断有效性
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
        setattr(model, AP_KEY, ap)
    return model
    