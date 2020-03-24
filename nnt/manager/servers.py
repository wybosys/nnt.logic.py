from ..config import NodeIsEnable
from ..core import app

_servers = {}

async def Start(cfg):
    if len(cfg):
        for e in cfg:        
            if not NodeIsEnable(e):
                continue
            if 'entry' not in e:
                print('server没有配置entry节点')
                continue
            
            t = app.App.shared().instanceEntry(e['entry'])            
            if not t:
                continue

            if t.config(e):
                _servers[t.id] = t                
                await t.start()            
            else:
                print(t.id + "配置失败")
    else:
        Stop()

def Wait():    
    for k in _servers:
        _servers[k].wait()

def Stop():
    global _servers
    for k in _servers:
        s = _servers[k]
        s.stop()
    _servers = {}
