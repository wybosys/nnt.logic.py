# 扩展python基础函数

def indexOf(lst, v):
    return lst.index(v) if v in lst else -1
    
def at(any, idx, default = None):
    try:
        return any[idx]
    except:
        return default
        