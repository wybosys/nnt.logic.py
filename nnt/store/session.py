from nnt.store.store import DbExecuteStat


class SORT:
    ASC = 1  # 升序
    DESC = -1  # 降序
    NONE = 0  # 不排序


class AbstractSession:

    def __init__(self):
        pass

    def reset(self) -> 'AbstractSession':
        return self

    def bind(self, clazz) -> 'AbstractSession':
        """绑定数据模型"""
        return self

    def close(self):
        pass

    def query(self, clazz) -> 'AbstractSession':
        return self

    def filter(self, fp, rule) -> 'AbstractSession':
        return self

    def filter(self, filter) -> 'AbstractSession':
        return self

    def sort(self, key, val: SORT = SORT.ASC) -> 'AbstractSession':
        return self

    def one(self):
        return None

    def first(self):
        return None

    def add(self, rcd, commit=True) -> bool:
        return False

    def commit(self):
        pass

    def all(self):
        return None

    def limit(self, n):
        return self

    def count(self) -> int:
        return 0

    def paged(self, m):
        self.limit(m.limit).skip(m.skips)
        return self.all()

    def skip(self, n):
        return self

    def update(self, m, commit=True) -> bool:
        return False

    def delete(self, m=None, commit=True) -> DbExecuteStat:
        return DbExecuteStat(remove=0)
