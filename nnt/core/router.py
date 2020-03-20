class IRouter:

    def __init__(self):
        super().__init__()

        # router的标记
        self.action = None

        # 接受配置文件的设置
        self.config = None
