import japronto
from .server import AbstractServer
from .transaction import Transaction, EmptyTransaction

class Rest(AbstractServer):
    
    def __init__(self):
        super().__init__()

    def instanceTransaction(self):
        """ 用来构造请求事物的类型 """
        return EmptyTransaction()
        