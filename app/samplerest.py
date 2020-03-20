from nnt.server import Rest
from .router import *
from .model.trans import Trans

class SampleRest(Rest):

    def __init__(self):
        super().__init__()
        self.routers.register(Sample())

    def instanceTransaction(self):
        return Trans()
        