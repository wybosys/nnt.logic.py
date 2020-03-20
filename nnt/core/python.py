# 扩展python基础函数

def indexOf(lst, v):
    return lst.index(v) if v in lst else -1
    
def at(any, idx, default = None):
    try:
        return any[idx]
    except:
        try:
            return getattr(any, idx)
        except:
            return default        
        
def delete(any, idx):
    try:
        del any[idx]
    except:
        pass
