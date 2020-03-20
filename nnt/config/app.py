class AppNodes:

    def __init__(self):
        super().__init__()

        # 全局配置节点
        self.config = None

        # 服务器节点
        self.server = None

        # 数据库节点
        self.dbms = None

        # 日志节点
        self.logger = None

        # 容器节点
        self.container = None

class DevopsNode:

    def __init__(self):
        super().__init__()

        self.client = True # 是否允许客户端访问本服务
        self.server = True # 是否允许服务端访问本服务
        self.allow = None # 白名单
        self.deny = None # 黑名单
