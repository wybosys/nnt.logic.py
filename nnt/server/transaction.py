from ..core.models import *
from ..core import time
from ..core.python import *

RESPONSE_SID = "X-NntLogic-SessionId"

class DeviceType:
    UNKNOWN = 0
    IOS = 1
    ANDROID = 2

class TransactionInfo:

    def __init__(self):
        super().__init__()

        # 客户端代码
        self.agent = None # 全小写
        self.ua = None # 原始ua

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
        self.model = False

        # 直接输出数据
        self.raw = False

        # 输出的类型
        self.type = None

class Transaction:

    def __init__(self):
        super().__init__()        

        # 超时定时器
        self._timeout = None

        # 运行在console中
        self.console = None

        # 环境信息
        self.info = TransactionInfo()

        # 是否把sid返回客户端
        self.responseSessionId = None

        # 静默模式，不输出回调
        self.quiet = False

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
        self.status = STATUS.UNKNOWN

        # 错误信息
        self.message = None

        # 额外数据
        self.payload = None

        # 输出和输入的model
        self.model = None

        # 基于哪个服务器运行
        self.server = None

        # 是否需要压缩
        self.gzip = False

        # 是否已经压缩
        self.compressed = False

        # 需要打开频控
        self.frqctl = False

        # 是否暴露接口（通常只有登录会设置为true)
        self.expose = False

        # 此次的时间
        self.time = time.DateTime.Now()

        # 执行权限
        self.ace = None

        # 默认启动超时处理
        self.waitTimeout()

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
        let ap = FindAction(r, self.call)
        if (!ap)
            return STATUS.ACTION_NOT_FOUND
        self.frqctl = ap.frqctl
        self.expose = ap.expose

        let clz = ap.clazz

        // 检查输入参数
        let sta = self.parser.checkInput(clz.prototype, self.params)
        if (sta != STATUS.OK)
            return sta

        // 填入数据到模型
        self.model = new clz()
        try {
            self.parser.fill(self.model, self.params, true, false)
        } catch (err) {
            self.model = null
            logger.fatal(err.toString())
            return STATUS.MODEL_ERROR
        }

        return STATUS.OK
    }

    // 恢复上下文，涉及到数据的恢复，所以是异步模式
    collect(): Promise<void> {
        return new Promise<void>(resolve => (resolve()))
    }

    // 验证
    needAuth(): boolean {
        return IsNeedAuth(self.model)
    }

    // 是否已经授权
    abstract auth(): boolean

    // 需要业务层实现对api的流控，避免同一个api瞬间调用多次，业务层通过重载lock/unlock实现
    // lock当即将调用api时由其他逻辑调用
    lock(): Promise<boolean> {
        return promise(true)
    }

    unlock() {
        // pass
    }

    // 同步模式会自动提交，异步模式需要手动提交
    implSubmit: (opt?: TransactionSubmitOption) => void
    private _submited: boolean
    private _submited_timeout: boolean

    async submit(opt?: TransactionSubmitOption) {
        if (self._submited) {
            if (!self._submited_timeout)
                logger.warn("数据已经发送")
            return
        }
        if (self._timeout) {
            CancelDelay(self._timeout)
            self._timeout = null
            self._submited_timeout = true
        }
        self._submited = true
        self._outputed = true
        if (self.hookSubmit) {
            try {
                await self.hookSubmit()
            } catch (err) {
                logger.exception(err)
            }
        }
        self.implSubmit(opt)

        // 只有打开了频控，并且此次是正常操作，才解锁
        if (self.frqctl && self.status != STATUS.HFDENY)
            self.unlock()
    }

    // 当提交的时候修改
    hookSubmit: () => Promise<void>

    // 输出文件
    implOutput: (type: string, obj: any) => void
    private _outputed: boolean

    output(type: string, obj: any) {
        if (self._outputed) {
            logger.warn("api已经发送")
            return
        }
        if (self._timeout) {
            CancelDelay(self._timeout)
            self._timeout = null
        }
        self._outputed = true
        self._submited = true
        self.implOutput(type, obj)
    }

    protected waitTimeout() {
        self._timeout = Delay(Config.TRANSACTION_TIMEOUT, () => {
            self._cbTimeout()
        })
    }

    // 部分api本来时间就很长，所以存在自定义timeout的需求
    timeout(seconds: number) {
        if (self._timeout) {
            CancelDelay(self._timeout)
            self._timeout = null
        }
        if (seconds == -1)
            return
        self._timeout = Delay(seconds, () => {
            self._cbTimeout()
        })
    }

    private _cbTimeout() {
        logger.warn("{{=it.action}} 超时", {action: self.action})
        self.status = STATUS.TIMEOUT
        self.submit()
    }
}

class EmptyTransaction(Transaction):

    def waitTimeout(self):
        pass    

    def sessionId(self) -> string:
        return None    

    def auth(self) -> bool:
        return False
