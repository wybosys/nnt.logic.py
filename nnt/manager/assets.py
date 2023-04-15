from ..core import url


class TYPE:
    JSON = "json"


# 资源目录
directory = None

url.RegisterScheme("assets",
                   lambda body:
                   directory + body
                   )
