from urllib.parse import unquote

from . import logger
from .python import *

# 当前运行的目录
ROOT = os.path.abspath('/')
HOME = os.getcwd()


def home():
    return HOME


# 自定义scheme的转换器
_schemes = {}


# 注册处理器
def RegisterScheme(scheme, proc):
    _schemes[scheme] = proc


def expand(url) -> str:
    """
    展开url, 如果包含 :// 则拆分成 scheme 和 body，再根绝 scheme 注册的转换器转换, 否则按照 / 来打断各个部分，再处理 ~、/ 的设置    
    """
    if indexOf(url, "://") != -1:
        ps = url.split("://")
        proc = _schemes[ps[0]]
        if proc is None:
            logger.fatal("没有注册该类型%s的处理器" % ps[0]);
            return None
        return proc(ps[1])

    ps = url.split('/')
    if ps[0] == "~":
        ps[0] = HOME
    elif ps[0] == "":
        if ROOT != '/':
            ps[0] = ROOT  # 主要支持windows
    else:
        return url

    return "/".join(ps)


def SmartDecodeSessionID(sid):
    if not sid:
        return sid
    if indexOf(sid, '%') == -1:
        return sid
    return unquote(sid)


# 注册普通的url请求
RegisterScheme("http", lambda body: body)
RegisterScheme("https", lambda body: body)
