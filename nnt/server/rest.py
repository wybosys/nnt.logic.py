import japronto
from .server import AbstractServer

class Rest(AbstractServer):
    
    def __init__(self):
        super().__init__()

    // 用来构造请求事物的类型
    protected instanceTransaction(): Transaction {
        return new EmptyTransaction();
    }    