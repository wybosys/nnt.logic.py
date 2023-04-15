from .rest import Rest
from ..core import logger


class Http2Server:

    def __init__(self, rest: Rest):
        super().__init__()
        self._rest = rest

    async def start(self):
        logger.fatal('暂不支持http2模式')
        return False

    def wait(self):
        pass
