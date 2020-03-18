# -*- coding:utf-8 -*-
from nnt.core.url import RegisterScheme

class TYPE:
    JSON = "json"

# 资源目录
directory = None

RegisterScheme("assets", 
lambda body:
    directory + body
)

