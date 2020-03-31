import shutil
import threading

from nnt.core import logger, url, cron
from nnt.core.python import *
from nnt.core.time import DateTime
from nnt.server.server import AbstractServer


class CronTask_Clean(cron.CronTask):

    def __init__(self, tpl):
        super().__init__(tpl)
        self.expire = 604800  # 1week
        self.path = None

    def __call__(self):
        super().__call__()
        if not os.path.exists(self.path):
            return
        threading.Thread(target=self._clean).start()

    def _clean(self):
        self._expire = DateTime.Current() - self.expire
        self._doclean(self.path)

    def _doclean(self, path):
        if os.path.isfile(path):
            st = os.stat(path)
            if st.st_ctime <= self._expire:
                logger.log('%s 文件过期被删除' % path)
                os.unlink(path)
        elif os.path.isdir(path):
            for e in os.listdir(path):
                self._doclean(path + '/' + e)


cron.Register('clean', CronTask_Clean)


class FileSystem(AbstractServer):

    def __init__(self):
        super().__init__()

    def config(self, cfg):
        super().config(cfg)
        if 'path' not in cfg:
            return False
        self.path = url.expand(cfg['path'])
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.cron = at(cfg, 'cron')
        return True

    async def start(self):
        await super().start()
        logger.info("启动 %s@rest" % self.id)
        if self.cron:
            for e in self.cron:
                k = at(e, 'idr')
                if not k:
                    logger.warn('cron没有配置idr')
                    continue
                obj = cron.Instance(k, e)
                if not obj:
                    logger.warn('启动 %s@cron 计划任务失败' % k)
                    continue
                obj['path'] = self.path
                cron.Add(obj)

    def move(self, src, dst):
        dst = self.path + '/' + dst
        try:
            shutil.move(src, dst)
        except Exception as err:
            logger.error(err)

    def copy(self, src, dst):
        dst = self.path + '/' + dst
        try:
            shutil.copy(src, dst)
        except Exception as err:
            logger.error(err)
