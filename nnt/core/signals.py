import time


class Object:
    def dispose(self):
        pass


class RefObject(Object):
    def __init__(self):
        super().__init__()
        self.__ref_cnt = 1

    def grab(self):
        self.__ref_cnt += 1

    def drop(self):
        self.__ref_cnt -= 1
        if self.__ref_cnt == 0:
            self.dispose()
            return None
        return self


class Tunnel:
    """用于穿透整个emit流程的对象"""

    def __init__(self):
        super().__init__()
        # 是否请求中断emit过程
        self.veto = False
        # 附加数据
        self.payload = None


class Slot:
    """插槽对象"""

    def __init__(self):
        super().__init__()
        # 重定向信号
        self.redirect = None
        # 回调函数
        self.cb = None
        # 回调的对象
        self.target = None
        # 激发者
        self.sender = None
        # 数据
        self.data = None
        # 延迟启动
        self.delay = 0
        # 穿透用的数据
        self.tunnel = None
        # 附加数据
        self.payload = None
        # 信号源
        self.signal = None
        # 激发频率限制 (emits per second)
        self.eps = 0
        # 调用几次自动解绑，默认为 null，不使用概设定
        self.count = 0
        self.emitedCount = 0
        # 其他
        self.__epstm = 0
        self.__veto = False

    def emit(self, data, tunnel):
        if self.eps:
            now = time.time()
            if self.__epstm == 0:
                self.__epstm = now
            else:
                el = now - self.__epstm
                if (1000 / el) > self.eps:
                    return
                self.__epstm = now
        self.data = data
        self.tunnel = tunnel
        self._doemit()

    def _doemit(self):
        if self.target:
            if self.cb:
                self.cb(self)
            elif not self.redirect:
                self.target.signals.emit(self.redirect, self.data)
        elif self.cb:
            self.cb(self)
        self.data = None
        self.tunnel = None
        self.emitedCount += 1

    @property
    def veto(self):
        return self.__veto

    @veto.setter
    def veto(self, b):
        self.__veto = b
        if self.tunnel:
            self.tunnel.veto = b


class Slots(Object):
    def __init__(self):
        super().__init__()
        # 所有者，会传递到 Slot 的 sender#
        self.owner = None
        # 信号源#
        self.signal = None
        # 其他
        self.__slots = []
        self.__blk = 0

    def dispose(self):
        super().dispose()
        self.clear()

    def clear(self):
        self.__slots.clear()

    def block(self):
        self.__blk += 1

    def unlock(self):
        self.__blk -= 1

    @property
    def isblocked(self):
        """是否已经阻塞"""
        return self.__blk != 0

    def add(self, s):
        """添加一个插槽"""
        self.__slots.append(s)

    def emit(self, data, tunnel):
        """对所有插槽激发信号
        @note 返回被移除的插槽的对象
        """
        r = set()
        if self.isblocked:
            return r

        for s in self.__slots.copy():
            if s.count and s.emitedCount >= s.count:
                continue

            s.signal = self.signal
            s.sender = self.owner
            s.emit(data, tunnel)

            if s.count and s.emitedCount >= s.count:
                self.__slots.remove(s)
                r.add(s.target)

            if s.veto:
                break

        return r

    def disconnect(self, cb, target):
        r = False
        for s in self.__slots.copy():
            if cb and s.cb != cb:
                continue
            if s.target == target:
                r = True
                self.__slots.remove(s)
        return r

    def find_connected_function(self, cb, target):
        for s in self.__slots:
            if s.cb == cb and s.target == target:
                return s
        return None

    def find_redirected(self, sig, target):
        for s in self.__slots:
            if s.redirect == sig and s.target == target:
                return s
        return None

    def is_connected(self, target):
        for s in self.__slots:
            if s.target == target:
                return True
        return False


class Signals(Object):
    def __init__(self, owner):
        super().__init__()
        self._owner = owner
        # 其他
        self.__invs = set()
        self.__slots = {}

    def dispose(self):
        super().dispose()
        self.clear()

    def clear(self):
        """清空"""
        # 反向断开连接
        for s in self.__invs:
            s.owner.signals.disconnectOfTarget(self.owner, False)
        self.__invs.clear()

        # 清空当前连接
        for sig in self.__slots:
            s = self.__slots[sig]
            s.clear()
        self.__slots.clear()

    def register(self, sig):
        """注册信号"""
        if not sig:
            print("不能注册一个空信号")
            return False

        if sig in self.__slots:
            return False

        ss = Slots()
        ss.signal = sig
        ss.owner = self.owner
        self.__slots[sig] = ss
        return True

    @property
    def owner(self):
        """信号主体"""
        return self._owner

    def once(self, sig, cb, target=None):
        """只连接一次"""
        r = self.connect(sig, cb, target)
        if r:
            r.count = 1
        return r

    def connect(self, sig, cb, target=None):
        """连接信号插槽"""
        if sig not in self.__slots:
            print("对象不存在信号 %s" % sig)
            return None
        ss = self.__slots[sig]

        s = ss.find_connected_function(cb, target)
        if s:
            return s

        s = Slot()
        s.cb = cb
        s.target = target
        ss.add(s)

        self.__inv_connect(target)
        return s

    def isConnected(self, sig):
        """该信号是否存在连接上的插槽"""
        if sig in self.__slots:
            ss = self.__slots[sig]
            return len(ss.__slots) != 0
        return False

    def redirect(self, sig1, sig2=None, target=None):
        """转发一个信号到另一个对象的信号"""
        if sig1 not in self.__slots:
            return None
        ss = self.__slots[sig1]
        s = ss.find_redirected(sig2, target)
        if s:
            return s

        s = Slot()
        s.redirect = sig2
        s.target = target
        ss.add(s)

        self.__inv_connect(target)
        return s

    def emit(self, sig, data=None, tunnel=None):
        """激发信号"""
        if sig not in self.__slots:
            print("对象不存在信号 %s" % sig)
            return

        ss = self.__slots[sig]
        targets = ss.emit(data, tunnel)
        if targets:
            for tgt in targets:
                if not self.isConnectedOfTarget(tgt):
                    self.__inv_disconnect(tgt)

    def disconnectOfTarget(self, target, inv=True):
        """断开连接"""
        if target == None:
            return

        for sig in self.__slots:
            s = self.__slots[sig]
            s.disconnect(None, target)

        if inv:
            self.__inv_disconnect(target)

    def disconnect(self, sig, cb, target=None):
        if sig not in self.__slots:
            return
        ss = self.__slots[sig]
        if cb == None and target == None:
            targets = set()
            for s in ss.__slots:
                if s.target:
                    targets.add(s.target)
            ss.clear()
            for tgt in targets:
                if not self.isConnectedOfTarget(tgt):
                    self.__inv_disconnect(tgt)
        else:
            if ss.disconnect(cb, target) and target and not self.isConnectedOfTarget(target):
                self.__inv_disconnect(target)

    def isConnectedOfTarget(self, target):
        for sig in self.__slots:
            s = self.__slots[sig]
            if s.is_connected(target):
                return True
        return False

    def block(self, sig):
        """阻塞一个信号，将不响应激发"""
        if sig in self.__slots:
            self.__slots[sig].block()

    def unblock(self, sig):
        if sig in self.__slots:
            self.__slots[sig].unblock()

    def isblocked(self, sig):
        if sig in self.__slots:
            return self.__slots[sig].isblocked
        return False

    def __inv_connect(self, target):
        if not target:
            return
        if target.signals == self:
            return
        target.signals.__invs.add(self)

    def __inv_disconnect(self, target):
        if not target or not hasattr(target, 'signals'):
            return
        if target.signals == self:
            return
        target.signals.__invs.remove(self)


class SObject(RefObject):
    def __init__(self):
        super().__init__()
        self._signals = None

    @property
    def signals(self):
        if not self._signals:
            self._signals = Signals(self)
        return self._signals

    def dispose(self):
        super().dispose()
        if self._signals:
            self._signals.dispose()
            self._signals = None
