from twisted.internet import reactor, endpoints
from twisted.web import proxy, server

from .server import AbstractServer
from ..core import kernel, logger
from ..core.python import *


class HomeResource(proxy.Resource):

    def getChild(self, path, request):
        if path not in self.children:
            print('没有命中 %s' % path)
            return super().getChild(path, request)
        return self.children[path]

    def getChildWithDefault(self, path, request):
        return self.getChild(path, request)


class Proxy(AbstractServer):

    def __init__(self):
        super().__init__()

        # 服务器端口配置
        self.listen = '127.0.0.1'
        self.port: int = 80

        # 代理的服务列表
        self.proxy = {}

    def config(self, cfg):
        if not super().config(cfg):
            return False

        if 'port' in cfg:
            self.port = cfg['port']

        if 'listen' in cfg:
            li = kernel.parse_socket_port_info(cfg['listen'])
            self.listen = li[0]
            if li[1]:
                self.port = li[1]
        if 'port' in cfg:
            self.port = cfg['port']

        self.proxy = at(cfg, 'proxy', self.proxy)
        return True

    async def start(self):
        home = HomeResource()
        for k in self.proxy:
            v = self.proxy[k]
            pi = kernel.parse_socket_port_info(v)
            if pi[1] is None:
                logger.warn('反向代理丢失%s的port配置' % k)
                continue
            t = proxy.ReverseProxyResource(pi[0], pi[1], b'')
            home.putChild(k.encode('utf-8'), t)

        cfg = [
            'tcp',
            'port=%d' % self.port,
            'interface=%s' % self.listen
        ]
        cfg = ':'.join(cfg)

        s = server.Site(home)
        endpoints.serverFromString(reactor, cfg).listen(s)
        reactor.run()

        logger.info("启动 %s@proxy" % self.id)
        await super().start()

    def stop(self):
        try:
            reactor.stop()
        except Exception as err:
            logger.exception(err)
        self.svr = None
