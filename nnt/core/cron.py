from apscheduler.schedulers.background import BackgroundScheduler

from . import logger
from .app import App, kSignalAppStopped


class _Cron:

    def __init__(self):
        super().__init__()
        self._schd = BackgroundScheduler()
        self._schd.start()

        App.shared().signals.connect(kSignalAppStopped, lambda s: self.stop())

    def stop(self):
        self._schd.shutdown()

    def add(self, cfg: str, proc):
        cfg = cfg.split(' ')
        kw = {
            'second': cfg[0],
            'minute': cfg[1],
            'hour': cfg[2],
            'day': cfg[3],
            'month': cfg[4],
            'week': cfg[5]
        }
        if len(cfg) == 7:
            kw['year'] = cfg[6]
        # 解析cfg
        self._schd.add_job(proc, 'cron', **kw)
        return self


_cron = _Cron()


def Second(d: int) -> str:
    return '%d * * * * *' % d


def Minute(d: int) -> str:
    return '0 %d * * * *' % d


def Hour(d: int) -> str:
    return '0 0 %d * * *' % d


def Day(d: int) -> str:
    return '0 0 0 %d * *' % d


class CronTaskTemplate:

    def __init__(self):
        super().__init__()
        # 任务类
        self.clazz = None
        # 此次绑定的执行函数
        self.proc = None


class CronTask:

    def __init__(self, tpl: CronTaskTemplate):
        super().__init__()
        self._tpl = tpl

        # 此次的配置
        self.cfg = None

    def __call__(self):
        if self._tpl:
            if self._tpl.proc:
                self._tpl.proc(self, self._tpl)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]


# 任务模板
_cron_templates = {}


def Register(idr: str, taskcls: type) -> CronTaskTemplate:
    """注册任务模板"""
    if idr in _cron_templates:
        print('已存在同名cron模板 %s' % idr)
    tpl = CronTaskTemplate()
    if not issubclass(taskcls, CronTask):
        tpl.clazz = CronTask
        tpl.proc = taskcls
    else:
        tpl.clazz = taskcls
    _cron_templates[idr] = tpl
    return tpl


def Find(idr: str) -> CronTaskTemplate:
    """查找任务模板"""
    if idr in _cron_templates:
        return _cron_templates[idr]
    return None


def Instance(idr: str, cfg: dict = None) -> CronTask:
    """实例化一个任务对象"""
    if idr not in _cron_templates:
        return None
    tpl = _cron_templates[idr]
    obj = tpl.clazz(tpl)
    if cfg:
        if type(cfg) != dict:
            print('cron配置错误')
            return None
        for k in cfg:
            obj[k] = cfg[k]
    return obj


def Add(task: CronTask):
    """添加一个任务"""
    _cron.add(task.cfg, task)


class CronTask_Counter(CronTask):
    """默认的打印计数的任务"""
    counter = 0

    def __init__(self, tpl):
        super().__init__(tpl)
        self.counter = None

    def __call__(self):
        super().__call__()
        if self.counter is not None:
            self.counter += 1
            logger.info('局部CronTask计数器 %d' % self.counter)
        else:
            CronTask_Counter.counter += 1
            logger.info('全局CronTask计数器 %d' % CronTask_Counter.counter)


# 注册内部任务
Register('counter', CronTask_Counter)
