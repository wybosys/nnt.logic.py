# -*- coding:utf-8 -*-

import os, json, shutil, sys
from ..core import signals as ss, logger
from ..core.url import *
from . import config, assets, loggers, dbmss, servers, containers
from ..core.python import *

kSignalAppStarted = '::nn::app::started'
kSignalAppStopped = '::nn::app::stopped'

class App(ss.SObject):

    _shared = None

    # 当前配置信息
    CurrentConfig = None

    @property
    def shared():
        return App._shared

    def __init__(self):
        super().__init__()
        
         # entry位于的目录
        self._entryDir = ""

        # 资源目录
        self._assetDir = ""

        # 绑定单件
        App._shared = self

        # 调用注册的全局事件
        RunHooks(BOOT)

        self.signals.register(kSignalAppStarted)
        self.signals.register(kSignalAppStopped)

    @staticmethod
    def LoadConfig(appcfg = "~/app.json", devcfg = "~/devops.json"):
        """加载程序配置"""
        appcfg = expand(appcfg)
        if devcfg:
            devcfg = expand(devcfg)

        # 读取配置信息
        if not os.path.exists(appcfg):
            print("读取配置文件失败")
            return None

        if devcfg and not os.path.exists(devcfg):        
            print("读取DEVOPS配置文件失败")
            return None        

        # 通过配置文件来启动服务端
        cfg = json.load(open(appcfg, 'r'))        

        # 处理输入参数
        argv = sys.argv

        # 判断是否直接执行指定服务
        directserveridx = indexOf(argv, '--server')
        if directserveridx != -1:
            directserver = argv[directserveridx + 1]
            # 运行指定的server
            if 'server' in cfg and cfg['server']:
                # 查找指定id的server
                for e in cfg['server']:
                    if e.id == directserver:
                        cfg['server'] = e
                        break
            # 其他配置清空
            cfg['container'] = []
            cfg['dbms'] = []

        config.DEBUG = indexOf(argv, "--debug")
        if config.DEBUG != -1:        
            logger.log("debug模式启动")
        else:
            config.DEVELOP = indexOf(argv, "--develop")
            if config.DEVELOP != -1:        
                logger.log("develop模式启动")
            else:
                config.PUBLISH = indexOf(argv, "--publish")
                if config.PUBLISH != -1:
                    logger.log("publish模式启动")
        config.DISTRIBUTION = not config.IsDebug()
        if config.DISTRIBUTION:
            logger.log("distribution模式启动")
        config.LOCAL = config.IsLocal()
        if config.LOCAL:
            logger.info("LOCAL 环境")
        config.DEVOPS = config.IsDevops()
        if config.DEVOPS:
            logger.info("DEVOPS 环境")
        config.DEVOPS_DEVELOP = config.IsDevopsDevelop()
        if config.DEVOPS_DEVELOP:
            logger.info("DEVOPS DEVELOP 环境")
        config.DEVOPS_RELEASE = config.IsDevopsRelease()
        if config.DEVOPS_RELEASE:
            logger.info("DEVOPS RELEASE 环境");

        # 设置为当前参数
        App.CurrentConfig = cfg

        # 读取系统配置
        c = cfg['config']
        if 'sidexpire' in c:
            config.SID_EXPIRE = c['sidexpire']
        if 'cidexpire' in c:
            config.CID_EXPIRE = c['cidexpire']
        if 'cache' in c:
            config.CACHE = expand(c['cache'])
        if 'https' in c:
            config.HTTPS = c['https']
        if 'http2' in c:
            config.HTTP2 = c['http2']
        if 'httpskey' in c:
            config.HTTPS_KEY = c['httpskey']
        if 'httpscert' in c:
            config.HTTPS_CERT = c['httpscert']
        if 'httpspfx' in c:
            config.HTTPS_PFX = c['httpspfx']
        if 'httpspasswd' in c:
            config.HTTPS_PASSWD = c['httpspasswd']
        if 'deskey' in c:
            config.DES_KEY = c['deskey']

        # 读取devops的配置
        if devcfg:
            cfg = json.load(open(devcfg, 'r'))
            if 'client' in cfg:
                config.CLIENT_ALLOW = cfg['client']
            if 'server' in cfg:
                config.SERVER_ALLOW = cfg['server']
            if 'allow' in cfg:
                config.ACCESS_ALLOW = cfg['allow']
            if 'deny' in cfg:
                config.ACCESS_DENY = cfg['deny']

        if not os.path.exists(config.CACHE):
            shutil.os.makedirs(config.CACHE)       

        return cfg    

    @property
    def entryDir(self):
        """entry位于的目录"""
        return self._entryDir

    @entryDir.setter
    def entryDir(self, val):
        self._entryDir = expand(val)

    @property
    def assetDir(self):
        """资源目录"""
        return self._assetDir

    @assetDir.setter
    def assetDir(self, val):
        self._assetDir = expand(val)

    async def start(self):
        # 设置资源管理器的目录
        assets.directory = self.assetDir        

        cfg = App.CurrentConfig
        if 'logger' in cfg:
            await loggers.Start(cfg['logger'])            
        if 'dbms' in cfg:
            await dbmss.Start(cfg.dbms);
            pass
        if 'server' in cfg:
            await servers.Start(cfg.server);
            pass
        if 'container' in cfg:
            await containers.Start(cfg.container);
            pass

        # 启动成功
        RunHooks(STARTED)
        self.signals.emit(kSignalAppStarted)
    
    async def stop(self):
        await servers.Stop();
        await dbmss.Stop();
        await loggers.Stop();
        await containers.Stop();

        RunHooks(STOPPED);
        self.signals.emit(App.EVENT_STOP)    

    def instanceEntry(self, entry):
        return None

    def containsEntry(self, entry):
        return False

# 用于挂住系统进程的钩子
BOOT = 'boot'
STARTED = 'sarted'
STOPPED = 'stopped'

# 全局钩子
_hooks = {}

def Hook(step, proc):
    if step not in _hooks:
        arr = []
        _hooks[step] = arr
    else:
        arr = _hooks[step]
    arr.append(proc)

def RunHooks(step):
    if step in _hooks:
        arr = _hooks[step]
        for e in arr:
            e()

# 处理entry的url转换
RegisterScheme("entry",
lambda body:
    App.shared.entryDir + body
)

# 处理clientSDK的url转换
RegisterScheme("sdk", 
lambda body:
    home() + "/src/" + body
)

RegisterScheme("cache", 
lambda body:
    config.CACHE + "/" + body
)
