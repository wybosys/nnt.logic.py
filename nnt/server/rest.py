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

        self.listen: str = '127.0.0.1'
        self.port: int = 80
        self.https: bool = False
        self.http2: bool = False
        self.timeout: float = 0
        self.imgsrv: str = None
        self.mediasrv: str = None
        self.router = None  # : string[] | IndexedObject;
        self. _hdl = None  # : http.Server | https.Server;
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
        cfg = {}
        if self.https:
            cfg = {}
            if config.HTTPS_PFX:
                cfg["pfx"] = url.expand(config.HTTPS_PFX)
            else:
                cfg["key"] = url.expand(config.HTTPS_KEY)
                cfg["cert"] = url.expand(config.HTTPS_CERT)
            if config.HTTPS_PASSWD:
                cfg["passphrase"] = config.HTTPS_PASSWD
            self._hdl = HttpsServer()
        elif self.http2:
            cfg['pfx'] = url.expand(config.HTTPS_PFX)
            cfg['spdy'] = {
                'protocols': ['h2', 'spdy/3.1', 'http/1.1'],
                'plain': False,
                'connection': {
                    'windowSize': 1024 * 1024,  # Server's window size
                    # **optional** if true - server will send 3.1 frames on 3.0 *plain* spdy
                    'autoSpdy31': False
                }
            }
            if config.HTTPS_PASSWD:
                cfg["passphrase"] = config.HTTPS_PASSWD
            this._hdl = Http2Server()
        else:
            this._hdl = HttpServer()
        if self.timeout:
            cfg['timeout'] = self.timeout
        cfg['port'] = self.port
        cfg['listen'] = self.listen
        r = await self._hdl.start(cfg)
        if not r:
            logger.info("启动 %s@rest 失败" % self.id)
        else:
            logger.info("启动 %s@rest" % self.id)
            self.onStart()


class HttpServer:

    async def start(self, cfg):
        return False


class Http2Server:

    async def start(self, cfg):
        return False


class HttpsServer:

    async def start(self, cfg):
        return False
