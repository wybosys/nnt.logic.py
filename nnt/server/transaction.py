from ..core import time, logger
from ..core.models import *
from ..core.proto import IsNeedAuth
from ..core.python import *
from ..core.router import FindAction
from ..manager import config

RESPONSE_SID = "X-NntLogic-SessionId"


class DeviceType:
    UNKNOWN = 0
    IOS = 1
    ANDROID = 2


class TransactionInfo:

    def __init__(self):
        super().__init__()

        # 客户端代码
        self.agent = None  # 全小写
        self.ua = None  # 原始ua

        # 访问的主机
        self.host = None
        self.origin = None

        # 客户端的地址
        self.addr = None

        # 来源
        self.referer = None
        self.path = None

        # 设备机型
        self._deviceType = None

    @property
    def deviceType(self):
        if self._deviceType != None:
            return self._deviceType
        if 'iphone' in self.agent:
            self._deviceType = DeviceType.IOS
        elif 'ipad' in self.agent:
            self._deviceType = DeviceType.IOS
        elif 'android' in self.agent:
            self._deviceType = DeviceType.ANDROID
        else:
            self._deviceType = DeviceType.UNKNOWN
        return self._deviceType


class TransactionSubmitOption:

    def __init__(self):
        super().__init__()

        # 仅输出模型
        self.model: bool = False

        # 直接输出数据
        self.raw: bool = False

        # 输出的类型
        self.type = None


class Transaction:

    def __init__(self):
        super().__init__()

        # 超时定时器
        self._timeout: time.Delayer = None

        # 运行在console中
        self.console: bool = None

        # 环境信息
        self.info = TransactionInfo()

        # 是否把sid返回客户端
        self.responseSessionId: str = None

        # 静默模式，不输出回调
        self.quiet: bool = False

        # 用来解析传入数据
        self.parser = None

        # 用来构建输出
        self.render = None

        # 映射到router的执行器中
        self.router = None
        self.call = None
        self._action = None

        # 参数
        self.params = None

        # 执行的结果
        self.status: int = STATUS.UNKNOWN

        # 错误信息
        self.message: str = None

        # 额外数据
        self.payload = None

        # 输出和输入的model
        self.model = None

        # 基于哪个服务器运行
        self.server = None

        # 是否需要压缩
        self.gzip: bool = False

        # 是否已经压缩
        self.compressed: bool = False

        # 需要打开频控
        self.frqctl: bool = False

        # 是否暴露接口（通常只有登录会设置为true)
        self.expose: bool = False

        # 此次的时间
        self.time = time.DateTime.Now()

        # 执行权限
        self.ace = None

        # 同步模式会自动提交，异步模式需要手动提交, (opt?: TransactionSubmitOption) => void
        self.implSubmit = None
        self._submited = False
        self._submited_timeout = False

        # 当提交的时候修改, () => Promise<void>
        self.hookSubmit = None

        # 输出文件 (type: string, obj: any) => void
        self.implOutput = None
        self._outputed = False

        # 默认启动超时处理
        self._waitTimeout()

    def sessionId(self):
        """返回事务用来区分客户端的id，通常业务中实现为sid"""
        return None

    def clientId(self):
        """获得同意个sid之下的客户端的id，和sid结合起来保证唯一性，即 sid.{cid}"""
        return self.params["_cid"]

    def instance(self, cls):
        """带上此次请求事务的参数实例化一个模型,通常业务层中会对params增加一些数据，来满足trans对auth、context的需求，如果直接new对象的化，就没办法加入这些数据"""
        return cls()

    def newOneClient(self):
        """是否是新连接上的客户端(包括客户端重启)"""
        return at(self.params, "_noc") == "1"

    @property
    def action(self):
        """动作"""
        return self._action

    @action.setter
    def action(self, act):
        self._action = act
        p = self._action.split(".")
        self.router = at(p, 0, "null").lower()
        self.call = at(p, 1, "null").lower()

    def modelize(self, r):
        """恢复到model, 返回错误码"""
        ap = FindAction(r.__class__, self.call)
        if not ap:
            return STATUS.ACTION_NOT_FOUND
        self.frqctl = ap.frqctl
        self.expose = ap.expose

        clz = ap.clazz

        # 检查输入参数
        sta = self.parser.checkInput(clz, self.params)
        if sta != STATUS.OK:
            return sta

        # 填入数据到模型
        self.model = clz()
        try:
            self.parser.fill(self.model, self.params, True, False)
        except Exception as err:
            self.model = None
            logger.fatal(err)
            return STATUS.MODEL_ERROR

        return STATUS.OK

    async def collect(self):
        """ 恢复上下文，涉及到数据的恢复，所以是异步模式 """
        pass

    def needAuth(self) -> bool:
        """ 此次请求需要验证 """
        return IsNeedAuth(self.model)

    def auth(self) -> bool:
        """ 是否已经授权 """
        return False

    def submit(self, opt: TransactionSubmitOption = None):
        if self._submited:
            if not self._submited_timeout:
                logger.warn("数据已经发送")
            return

        if self._timeout:
            self._timeout.stop()
            self._timeout = None
            self._submited_timeout = True

        self._submited = True
        self._outputed = True
        if self.hookSubmit:
            try:
                self.hookSubmit()
            except Exception as err:
                logger.exception(err)
        self.implSubmit(self, opt)

    def output(self, type, obj):
        if self._outputed:
            logger.warn("api已经发送")
            return

        if self._timeout:
            self._timeout.stop()
            self._timeout = None

        self._outputed = True
        self._submited = True
        self.implOutput(self, type, obj)

    def _waitTimeout(self):
        self._timeout = time.Delayer(
            config.TRANSACTION_TIMEOUT, self._cbTimeout)
        self._timeout.start()

    def timeout(self, seconds):
        """ 部分api本来时间就很长，所以存在自定义timeout的需求 """
        if self._timeout:
            self._timeout.stop()
            self._timeout = None
        if seconds == -1:
            return
        self._timeout = time.Delayer(seconds, self._cbTimeout)
        self._timeout.start()

    def _cbTimeout(self):
        logger.warn("%s 超时" % self.action)
        self._timeout = None
        self.status = STATUS.TIMEOUT
        self.submit()


class EmptyTransaction(Transaction):

    def waitTimeout(self):
        pass

    def sessionId(self) -> str:
        return None

    def auth(self) -> bool:
        return False


def ConsoleSubmit(self):
    cb = self.params["__callback"]
    cb(self)


def ConsoleOutput(self, type: str, obj):
    cb = self.params["__callback"]
    self.payload = obj
    cb(self)
