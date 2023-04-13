import platform

from .kvredis import KvRedis
from .kvdbm import KvDbm

if platform.system() != "Windows":
    from .kvlevel import KvLevel
