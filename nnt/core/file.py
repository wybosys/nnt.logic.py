import mimetypes
import magic


class Mime:
    @staticmethod
    def Type(path: str, default: str = None) -> str:
        r = mimetypes.guess_type(path)[0]
        if r != None:
            return r
        if path.endsWith("amr"):
            return "audio/amr"
        return default

    @staticmethod
    def Extension(typ: str, default: str = None) -> str:
        r = mimetypes.guess_extension(typ)
        if r != None:
            return r
        if typ == "audio/amr":
            return "amr"
        return default

    @staticmethod
    def TypeOfFile(path: str, default: str = None) -> str:
        try:
            return magic.from_file(path, True)
        except:
            pass
        return default

    @staticmethod
    def TypeOfBuffer(buf: bytearray, default: str = None) -> str:
        try:
            return magic.from_buffer(buf, True)
        except:
            pass
        return default
