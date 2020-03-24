from ..core.file import *
import os
import datetime


class RespFile:
    """  专用来返回的文件对象 """

    @staticmethod
    def Regular(file: str, typ: str = None) -> 'RespFile':
        r = RespFile()
        if not typ:
            typ = Mime.Type(file)
        r._file = file
        r.type = typ
        r._stat = os.stat(file)
        return r

    @staticmethod
    def Buffer(buf: bytearray, typ: str = None) -> 'RespFile':
        r = RespFile()
        r.type = typ
        r._buf = buf
        return r

    @staticmethod
    def Plain(txt: str, typ: str = None) -> 'RespFile':
        r = RespFile()
        r.type = typ
        r._buf = txt.encode('utf-8')
        return r

    @property
    def length(self) -> int:
        if self._stat:
            return self._stat.st_size
        if self._buf:
            return self._buf.length
        return 0

    def __init__(self):
        super().__init__()

        self._file: str = None
        self._buf: bytearray = None
        self.type: str = None
        self._stat: os.stat_result = None
        self._cachable: bool = True
        self._downloadfile: str = None
        self._expire = None

    @property
    def file(self) -> str:
        if self._file:
            return self._file
        if self._downloadfile:
            return self._downloadfile
        return None

    @property
    def stat(self) -> os.stat_result:
        return self._stat

    @property
    def cachable(self) -> bool:
        return self._stat != None

    def asDownload(self, filename: str):
        self._downloadfile = filename
        return self

    @property
    def expire(self):
        """过期时间，默认为1年"""
        if self._expire:
            return self._expire
        self._expire = datetime.datetime.now() + datetime.timedelta(days=365)
        return self._expire

    @property
    def download(self) -> bool:
        return self._downloadfile != None
