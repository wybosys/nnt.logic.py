class AbstractDbms:
    def __init__(self):
        super().__init__()

        # 唯一标记
        self.id = None

    # 配置
    def config(self, cfg) -> bool:
        self.id = cfg["id"]
        return True

    # 创建一个过程
    def session(self) -> "AbstractSession":
        return None

    # 打开连接
    async def open(self):
        pass

    # 关闭连接
    def close(self):
        pass


# 数据库执行的情况
class DbExecuteStat:
    def __init__(self, insert=0, update=0, remove=0):
        super().__init__()

        # 增加行数
        self.insert = insert

        # 修改行数
        self.update = update

        # 删除行数
        self.remove = remove


# 定义用于返回查询结果的类型
RecordObject = dict
