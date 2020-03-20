# -*- coding:utf-8 -*-

class AbstractDbms:

    def __init__(self):
        super().__init__()

        # 唯一标记
        self.id = None

    # 配置
    def config(self, cfg):
        this.id = cfg['id']
        return True

    # 打开连接
    def open(self): pass

    # 关闭连接
    def close(self): pass

    # 事务处理
    def begin(self): pass

    def complete(self): pass

    def cancel(self): pass

# 数据库执行的情况
class DbExecuteStat:

    def __init__(self):
        super().__init__()

        # 增加行数
        self.insert = 0

        # 修改行数
        self.update = 0

        # 删除行数
        self.remove = 0
