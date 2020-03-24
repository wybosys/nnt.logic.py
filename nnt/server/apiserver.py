class IApiServer:

    def __init__(self):
        super().__init__()

        # 用来给api提供图床，设置的是对应服务的srvid
        self.imgsrv: str = None

        # 用来给api提供视频、音频池
        self.mediasrv: str = None


class IHttpServer:

    # 返回内部实现的http原始句柄 http.Server
    def httpserver(self):
        return None
