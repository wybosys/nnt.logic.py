import nnt.core.router as r
from ..model import *
from nnt.core import time

class Sample(r.IRouter):

    def __init__(self):
        super().__init__()
        self.action = "sample"

    @r.action(Echoo)
    def echo(self, trans):
        m = trans.model
        m.output = m.input
        m.time = time.DateTime.Now()
        m.json = {}
        m.map.set('a0', 0).set('b1', 1)
        m.array.push(0, 1, 2, 3)
        trans.submit()
        