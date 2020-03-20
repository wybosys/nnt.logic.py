from ..core.python import *

class AbstractServer:

    def __init__(self):
        super().__init__()

        # 服务器的配置id
        self.id = None

    # 配置服务
    def config(self, cfg):
        if not at(cfg, 'id'):
            return False
        self.id = cfg['id']
        return True
    
    async def start(self):
        """ 启动服务 """
        pass
    
    async def stop(self):
        """ 停止服务 """
        pass
    
    def _onStart(self):
        pass    

    def _onStop(self):
        pass

class IConsoleServer:
    """如果需要在业务中的api调用某一个服务(使用Servers.Call函数)则目标server必须实现此接口"""
    
    def invoke(self, params, req, rsp, ac = None):
        """ 通过控制台执行
            @params 调用参数
            @req 请求对象
            @rsp 响应对象
            @ac 特殊权限"""
        pass
