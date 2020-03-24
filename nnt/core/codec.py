import io
import gzip


def gzip_compress(plain: str) -> bytes:
    buf = io.BytesIO()
    g = gzip.GzipFile(fileobj=buf, mode='wb')
    g.write(plain.encode('utf-8'))
    g.close()    
    return buf.getvalue()
