import platform

from .kvdbm import KvDbm
from .kvredis import KvRedis

if platform.system() != "Windows":
    from .kvlevel import KvLevel
