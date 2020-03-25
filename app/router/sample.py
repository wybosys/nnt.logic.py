import nnt.core.router as r
from nnt.core import time
from ..model import *


class Sample(r.IRouter):

    def __init__(self):
        super().__init__()
        self.action = "sample"

    @r.action(Echoo)
    def echo(self, trans):
        m: Echoo = trans.model
        m.output = m.input
        m.time = time.DateTime.Now()
        m.json = {}
        m.map['a0'] = 0
        m.array.extend([1, 2, 3, 4])
        trans.submit()
