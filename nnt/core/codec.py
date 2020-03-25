import gzip
import io


def gzip_compress(plain) -> bytes:
    buf = io.BytesIO()
    g = gzip.GzipFile(fileobj=buf, mode='wb')
    if type(plain) == str:
        g.write(plain.encode('utf-8'))
    else:
        g.write(plain)
    g.close()
    return buf.getvalue()
