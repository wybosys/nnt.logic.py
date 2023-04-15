from nnt.server import Rest
from .model.trans import Trans
from .router import *


class SampleRest(Rest):

    def __init__(self):
        super().__init__()
        self.routers.register(Sample())

    def instanceTransaction(self):
        return Trans()
