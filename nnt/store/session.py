class AbstractSession:

    def __init__(self):
        pass

    def close(self):
        pass

    def query(self, clazz) -> 'AbstractSession':
        return self

    def filter(self, fp, rule) -> 'AbstractSession':
        return self

    def filter(self, filter) -> 'AbstractSession':
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
