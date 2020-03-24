import japronto
import socket
import multiprocessing
from .server import *
from .apiserver import *
from .transaction import Transaction, EmptyTransaction
from ..core import logger, app, url
from ..core.python import *
from ..manager import config
from .routers import *


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


class Rest(AbstractServer, IRouterable, IConsoleServer, IApiServer, IHttpServer):

    def __init__(self):
        super().__init__()
        self. _hdl = None

    def instanceTransaction(self) -> Transaction:
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

    def invoke(self, params, req, rsp, ac=None):
        self._hdl.invoke(self, params, req, rsp, ac)

    def onBeforeInvoke(self, trans: Transaction):
        """处理请求前"""
        pass

    def onAfterInvoke(self, trans: Transaction):
        pass

    def doInvoke(self, t: Transaction, params, req, rsp, ac=None):
        if req and rsp:
            t.payload = {req: req, rsp: rsp}
            t.implSubmit = TransactionSubmit
            t.implOutput = TransactionOutput
        else:
            t.implSubmit = ConsoleSubmit
            t.implOutput = ConsoleOutput

        listen = at(params, '_listen')
        if listen == "1":
            self._routers.listen(t)
        elif listen == "2":
            self._routers.unlisten(t)
        else:
            self._routers.process(t)


class JaprontoNonblockingApplication(japronto.Application):

    def _run(self, *, host, port, worker_num=None, reloader_pid=None, debug=None):
        self._debug = debug or self._debug
        if self._debug and not self._log_request:
            self._log_request = self._debug

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        os.set_inheritable(sock.fileno(), True)

        self.workers = set()

        terminating = False

        def stop(sig=None, frame=None):
            nonlocal terminating
            if reloader_pid and sig == signal.SIGHUP:
                print('Reload request received')
            elif not terminating:
                terminating = True
                print('Termination request received')
            for worker in self.workers:
                worker.terminate()

        for _ in range(worker_num or 1):
            worker = multiprocessing.Process(
                target=self.serve,
                kwargs=dict(sock=sock, host=host, port=port,
                            reloader_pid=reloader_pid))
            worker.daemon = True
            worker.start()
            self.workers.add(worker)

        # prevent further operations on socket in parent
        sock.close()

    def wait_all(self):
        for worker in self.workers:
            worker.join()
        self.workers.clear()

    def stop_all(self):
        for worker in self.workers:
            worker.terminate()


class JaprontoResponse:

    def __init__(self, req):
        super().__init__()
        self._req = req
        self._headers = {}

    def setHeader(self, k, v):
        self._headers[k] = v


class HttpServer:

    def __init__(self, rest: Rest):
        super().__init__()
        self._hdl = JaprontoNonblockingApplication()
        self._rest = rest

        route = '/'
        self._hdl.router.add_route(route, self._dowork)

        # 动态增加目录监听
        n = 0
        while n < 128:
            n += 1
            route += '{_p%d}/' % n
            self._hdl.router.add_route(route, self._dowork)

    async def start(self):
        self._hdl.run(host=self._rest.listen, port=self._rest.port)
        return True

    def wait(self):
        self._hdl.wait_all()

    def stop(self):
        self._hdl.stop_all()

    def _dowork(self, req):
        rsp = JaprontoResponse(req)

        # 打开跨域支持
        rsp.setHeader("Access-Control-Allow-Origin", "*")
        rsp.setHeader("Access-Control-Allow-Credentials", "true")
        rsp.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        # 直接对option进行成功响应
        if req.method == "OPTIONS":
            if at(req.headers, "access-control-request-headers"):
                rsp.setHeader("Access-Control-Allow-Headers",
                              req.headers["access-control-request-headers"])
            if at(req.headers, "access-control-request-method") == "POST":
                rsp.setHeader("Content-Type", "multipart/form-data")
            rsp.writeHead(204)
            rsp.end()
            return

        # 处理url请求
        url: str = req.path
        logger.log(req.path)
        print(req.body)

        # 支持几种不同的路由格式
        # ?action=xxx.yyy&params
        # $$/xxx.yyy$params
        # xxx/yyy&params
        params = req.query.copy()
        # 为了支持第三方平台通过action同名传递动作
        if url.startswith("/$$/") or url.startswith("/action/"):
            p = url.split("/")
            pl = len(p)
            i = 0
            while i < pl:
                k = p[i]
                v = p[i+1]
                params[k] = v
                i += 2
        else:
            p = url.split('/')
            pl = len(p)
            if pl >= 2:
                r = p[pl - 2]
                a = p[pl - 1]
                params['action'] = r + '.' + a

        # 如果是post请求，则处理一下form数据
        if req.method == "POST":
            # 如果是multipart-form得请求，则不适用于处理buffer
            ct = at(req.headers, "content-type")
            if not ct:
                ct = 'application/json'
            if 'form' in ct:
                pass
            else:
                pass
        else:
            self.invoke(params, req, rsp)

    def invoke(self, params, req, rsp, ac=None):
        action = at(params, "action")
        if not action:
            rsp.writeHead(400)
            rsp.end()
            return

        t = self._rest.instanceTransaction()
        try:
            t.ace = ac
            t.server = self._rest
            t.action = action
            t.params = params

            # 整理数据
            if req:  # 如果是通过console调用，则req会为none
                if "_agent" in params:
                    t.info.ua = params["_agent"]
                else:
                    t.info.ua = at(req.headers, 'user-agent')
                if not t.info.ua:
                    t.info.ua = 'unknown'
                t.info.agent = t.info.ua.lower()
                t.info.host = at(req.headers, 'host')
                t.info.origin = at(req.headers, 'origin')
                t.info.referer = at(req.headers, 'referer')
                t.info.path = req.path
                if 'accept-encoding' in req.headers:
                    t.gzip = 'gzip' in req.headers['accept-encoding']

                # 获取客户端真实ip
                if not t.info.addr:  # docker
                    t.info.addr = at(req.headers, 'http_x_forwarded_for')
                if not t.info.addr:  # proxy
                    t.info.addr = at(req.headers, 'x-forwarded-for')
                if not t.info.addr:  # normal
                    t.info.addr = req.connection.remoteAddress

            # 绑定解析器
            t.parser = FindParser(params['_pfmt'])  # _pfmt parser format 预留关键字
            t.render = FindRender(params['_rfmt'])  # _ofmt render format 预留关键字

            # 处理调用
            self._rest.onBeforeInvoke(t)
            self._rest.doInvoke(t, params, req, rsp, ac)
            self._reset.onAfterInvoke(t)
        except Exception as err:
            logger.exception(err)
            t.status = STATUS.EXCEPTION
            t.submit()


class Http2Server:

    def __init__(self, rest: Rest):
        super().__init__()
        self._rest = rest

    async def start(self):
        logger.fatal('暂不支持http2模式')
        return False

    def wait(self):
        pass


class HttpsServer:

    def __init__(self, rest: Rest):
        super().__init__()
        self._rest = rest

    async def start(self):
        logger.fatal('暂不支持https模式')
        return False

    def wait(self):
        pass
