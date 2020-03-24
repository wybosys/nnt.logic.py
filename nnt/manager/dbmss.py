from ..config import NodeIsEnable
from ..core import app

_dbs = {}

async def Start(cfg):
    if len(cfg):
        for e in cfg:
            if not NodeIsEnable(e):
                continue
            if 'entry' not in e:
                print('db没有配置entry节点')
                continue

            t = app.App.shared().instanceEntry(e['entry'])            
            if not t:
                continue

            if t.config(e):
                await t.open()
                _dbs[t.id] = t
            else:
                print(t.id + "配置失败")
    else:
        Stop()

def Stop():
    global _dbs
    for k in _dbs:
        db = _dbs[k]
        db.close()
    _dbs = {}

# 获得指定名称的数据库连接
def Find(id):
    return _dbs[id] if id in _dbs else None
