from .kernel import *
from .python import *
from .url import expand


class DevopsConfig:

    def __init__(self):
        super().__init__()

        self.path: str = None
        self.client: bool = False
        self.domain: str = None

    def unserial(self, json):
        self.path = at(json, 'path', '')
        self.client = at(json, 'client', False)
        self.domain = self.path[16:]


CONFIG_FILE = expand('~/devops.json')

_devopsconfig = DevopsConfig()
_devopsconfig.unserial(toJsonObject(get_file_content(CONFIG_FILE)))


def GetPath() -> str:
    return _devopsconfig.path


def GetDomain() -> str:
    return _devopsconfig.domain
