import os

# DEBUG模式
DEBUG = False

# DEVELOP模式，和debug的区别，develop用来部署开发服务器，debug用来做本地开发，会影响到app.json中对服务器的启动处理
DEVELOP = False

# PUBLISH模式，和release类似，除了会使用线上配置外，其他又和develop一致
PUBLISH = False

# 正式版模式
DISTRIBUTION = True

# 本地模式
LOCAL = False

# 容器部署
DEVOPS = False

# 内网测试容器部署
DEVOPS_DEVELOP = False

# 外网容器部署
DEVOPS_RELEASE = True

# sid过期时间，此框架中时间最小单位为秒
SID_EXPIRE = 86400

# clientid 过期时间
CID_EXPIRE = 600

# model含有最大fields的个数
MODEL_FIELDS_MAX = 100

# transaction超时时间
TRANSACTION_TIMEOUT = 20

# 是否允许客户端访问
CLIENT_ALLOW = False

# 是否允许服务端访问
SERVER_ALLOW = True

# 白名单
ACCESS_ALLOW = []

# 黑名单
ACCESS_DENY = []

# 默认的https证书配置
HTTPS = None
HTTP2 = None
HTTPS_KEY = None
HTTPS_CERT = None
HTTPS_PFX = None
HTTPS_PASSWD = None

# 用于DES的密钥，只能在开服时修改，不然修改前产生的数据都会解密失败
DES_KEY = "0i923,dfau9o8"

# 服务端缓存目录
CACHE = "cache"

# 最大下载文件的大小
FILESIZE_LIMIT = 10485760  # 10M


# 判断是否是开发版
def IsDebug():
    return DEBUG or DEVELOP or PUBLISH


# 是否是正式版
def IsRelease():
    return DISTRIBUTION


def DebugValue(d, r):
    return r if DISTRIBUTION else d


# 支持DEVOPS的架构判断
def IsDevops():
    return os.getenv('DEVOPS') != None


def IsDevopsDevelop():
    return os.getenv('DEVOPS') != None and os.getenv('DEVOPS_RELEASE') == None


def IsDevopsRelease():
    return os.getenv('DEVOPS_RELEASE') != None


def IsLocal():
    return os.getenv('DEVOPS') == None
