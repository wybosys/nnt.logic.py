import japronto
from .server import AbstractServer
from .transaction import Transaction, EmptyTransaction
from ..core import logger, app, url
from ..core.python import *
from ..manager import config
from .routers import Routers


class RestResponseData:

    def __init__(self):
        super().__init__()
        self.contentType: str = None
        self.content: str = None


class RestNode:

    def __init__(self):
        super().__init__()

        # 服务器端口配置
        self.listen: str = '127.0.0.1'
        self.port: int = 80

        # 安全设置
        self.https: bool = False

        # http2 支持
        self.http2: bool = False

        # 图片服务器的id，Rest服务如果需要管理图片，则必须配置此参数指向图片服务器的id，如果该图片服务器是其他服务器的代理，则也是会有一个id
        self.imgsrv: str = None

        # 媒体服务器
        self.mediasrv: str = None

        # 通过配置加载的路由器
        self.router = None  # string[] | IndexedObject router的列表或者 router:config 的对象

        # 超时s
        self.timeout: float = 0


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
        self. _hdl = None
        self._routers = Routers()

    @property
    def routers(self) -> Routers:
        return self._routers

    def instanceTransaction(self):
        """ 用来构造请求事物的类型 """
        return EmptyTransaction()

    def config(self, cfg) -> bool:
        if not super().config(cfg):
            return False
        if not at(cfg, 'port'):
            return False
        self.listen = None
        if at(cfg, 'listen') and at(cfg, 'listen') != "*":
            self.listen = cfg['listen']
        else:
            self.listen = '127.0.0.1'
        self.port = cfg['port']
        self.imgsrv = at(cfg, 'imgsrv')
        self.mediasrv = at(cfg, 'mediasrv')
        self.https = nonnull1st(False, at(cfg, 'https'), config.HTTPS)
        self.http2 = nonnull1st(False, at(cfg, 'http2'), config.HTTP2)
        if self.https or self.http2:
            if config.HTTPS_PFX:
                pass
            elif config.HTTPS_KEY and config.HTTPS_CERT:
                pass
            else:
                logger.warn("没有配置https的证书")
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
                        logger.warn("路由配置出错 %s" % e)
                        return False
                    self._routers.register(router)

        return True

    def httpserver(self):
        return self._hdl

    async def start(self):
        if self.https:
            self._hdl = HttpsServer()
        elif self.http2:
            self._hdl = Http2Server()
        else:
            self._hdl = HttpServer()
        r = await self._hdl.start(self)
        if not r:
            logger.info("启动 %s@rest 失败" % self.id)
        else:
            logger.info("启动 %s@rest" % self.id)
            self.onStart()

    def onStart(self):
        pass

    def onStop(self):
        pass


class HttpServer:

    def __init__(self):
        super().__init__()
        self._hdl = japronto.Application()

    async def start(self, svr: Rest):
        self._hdl.run(host=svr.listen, port=svr.port)
        return True


class Http2Server:

    async def start(self, svr: Rest):
        logger.fatal('暂不支持http2模式')
        return False


class HttpsServer:

    async def start(self, svr: Rest):
        logger.fatal('暂不支持https模式')
        return False
