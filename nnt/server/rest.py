import japronto
from .server import AbstractServer
from .transaction import Transaction, EmptyTransaction
from ..core import logger, app
from ..core.python import *
from ..manager import config


class RestResponseData:

    def __init__(self):
        super().__init__()
        self.contentType: str = None
        self.content: str = None


class RestNode:

    def __init__(self):
        super().__init__()

        # 服务器端口配置
        self.listen: str
        self.port: int

        # 安全设置
        self.https: bool

        # http2 支持
        self.http2: bool

        # 图片服务器的id，Rest服务如果需要管理图片，则必须配置此参数指向图片服务器的id，如果该图片服务器是其他服务器的代理，则也是会有一个id
        self.imgsrv: str

        # 媒体服务器
        self.mediasrv: str

        # 通过配置加载的路由器
        self.router  # string[] | IndexedObject router的列表或者 router:config 的对象

        # 超时s
        self.timeout: float


class TransactionPayload:

    def __init__(self):
        super().__init__()

        # rest服务收到的请求
        self.req  # : http.IncomingMessage;

        # 用来发送响应的数据
        self.rsp  # : http.ServerResponse;



class Rest(AbstractServer):

    def __init__(self):
        super().__init__()

        self.listen: str
        self.port: int
        self.https: bool
        self.http2: bool
        self.timeout: float
        self.imgsrv: str
        self.mediasrv: str
        self.router #: string[] | IndexedObject;
        self. _hdl #: http.Server | https.Server;

    def instanceTransaction(self):
        """ 用来构造请求事物的类型 """
        return EmptyTransaction()

    def config(self, cfg)-> bool:
        if not super().config(cfg):
            return False
        if not at(cfg, 'port'):
            return False
        self.listen = None
        if at(cfg, 'listen') and at(cfg, 'listen') != "*":
            self.listen = cfg['listen']        
        self.port = cfg['port']
        self.imgsrv = at(cfg, 'imgsrv')
        self.mediasrv = at(cfg, 'mediasrv')
        self.https = nonnull1st(False, cfg['https'], config.HTTPS)
        self.http2 = nonnull1st(False, cfg['http2'], config.HTTP2)
        if self.https or self.http2:
            if config.HTTPS_PFX:
                pass
            elif config.HTTPS_KEY and config.HTTPS_CERT:
                pass
            else:
                logger.warn("没有配置https的证书");
                return False
        self.timeout = at(cfg, 'timeout')

        # 读取配置文件中配置的router
        if at(cfg, 'router'):
            self.router = cfg['router']

            if type(self.router) == list:
                for e in self.router:
                    router = app.App.shared().instanceEntry(e)                    
                    if not router:
                        logger.warn("没有找到该实例类型 %s" % e)
                        return False
                    else:
                        self._routers.register(router)
            else:
                for e in self.router:
                    router = app.App.shared().instanceEntry(e)
                    if not router:
                        logger.warn("没有找到该实例类型 %s" % e)
                        return False
                    cfg = self.router[e]                    
                    if not router.config(cfg):
                        logger.warn("服务配置出错 %s" % e)
                        return False
                    self._routers.register(router)

        return True

