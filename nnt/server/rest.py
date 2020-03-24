import japronto
import socket
import multiprocessing
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
            await super().start()

    def wait(self):        
        self._hdl.wait()

    async def stop(self):
        self._hdl.stop()
        await super().stop()

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

    def stop_all(self):
        for worker in self.workers:
            worker.terminate()
        self.workers.clear()

class HttpServer:

    def __init__(self):
        super().__init__()
        self._hdl = JaprontoNonblockingApplication()

    async def start(self, svr: Rest):
        self._hdl.run(host=svr.listen, port=svr.port)
        return True

    def wait(self):
        self._hdl.wait_all()

    def stop(self):
        self._hdl.stop_all()


class Http2Server:

    async def start(self, svr: Rest):
        logger.fatal('暂不支持http2模式')
        return False

    def wait(self):
        pass

class HttpsServer:

    async def start(self, svr: Rest):
        logger.fatal('暂不支持https模式')
        return False

    def wait(self):
        pass
