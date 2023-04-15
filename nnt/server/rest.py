from .apiserver import *
from .http2server import Http2Server
from .httpsserver import HttpsServer
from .parser import *
from .render import *
from .routers import *
from .server import *
from .transaction import *
from ..core import app, kernel

if sys.version_info.minor <= 7:
    from .httpserver_japronto import HttpServer
else:
    from .httpserver_tornado import HttpServer


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

    def __init__(self, req=None, rsp=None):
        super().__init__()

        # rest服务收到的请求
        self.req = req  # : http.IncomingMessage;

        # 用来发送响应的数据
        self.rsp = rsp  # : http.ServerResponse;


class Rest(AbstractServer, IRouterable, IConsoleServer, IApiServer, IHttpServer):

    def __init__(self):
        super().__init__()
        self._hdl = None

    def instanceTransaction(self) -> Transaction:
        """ 用来构造请求事物的类型 """
        return EmptyTransaction()

    def config(self, cfg) -> bool:
        if not super().config(cfg):
            return False

        if 'listen' in cfg:
            li = kernel.parse_socket_port_info(cfg['listen'])
            self.listen = li[0]
            if li[1]:
                self.port = li[1]
        if 'port' in cfg:
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
            self._hdl = HttpsServer(self)
        elif self.http2:
            self._hdl = Http2Server(self)
        else:
            self._hdl = HttpServer(self)
        r = await self._hdl.start()
        if not r:
            logger.info("启动 %s@rest 失败" % self.id)
        else:
            logger.info("启动 %s@rest" % self.id)
            await super().start()

    def wait(self):
        self._hdl.wait()

    def stop(self):
        self._hdl.stop()
        super().stop()

    async def invoke(self, params, req, rsp, ac=None):
        await self._hdl.invoke(self, params, req, rsp, ac)

    def onBeforeInvoke(self, trans: Transaction):
        """处理请求前"""
        pass

    def onAfterInvoke(self, trans: Transaction):
        pass

    async def doInvoke(self, t: Transaction, params, req, rsp, ac=None):
        if req and rsp:
            t.payload = TransactionPayload(req, rsp)
            t.implSubmit = self._hdl.submit
            t.implOutput = self._hdl.output
        else:
            t.implSubmit = ConsoleSubmit
            t.implOutput = ConsoleOutput

        listen = at(params, '_listen')
        if listen == "1":
            await self._routers.listen(t)
        elif listen == "2":
            await self._routers.unlisten(t)
        else:
            await self._routers.process(t)


# 注册支持的输出格式
RegisterRender("json", Json())

# 注册支持的输入格式
RegisterParser("jsobj", Jsobj())
