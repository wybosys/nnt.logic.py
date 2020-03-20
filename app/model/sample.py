import nnt.core.proto as cp
import nnt.store.proto as sp


@cp.model([cp.enum])
class EchoType:
    TEST = 88


@cp.model()
class Echoo:

    input = cp.string(1, [cp.input], "输入")
    output = cp.string(2, [cp.output], "输出")
    time = cp.integer(3, [cp.output], "服务器时间")
    json = cp.json(4, [cp.output])
    map = cp.map(5, cp.cp.string_t, cp.integer_t, [cp.output])
    array = (6, cp.double_t, [cp.cp.output])
    enm = cp.enumerate(7, EchoType, [cp.cp.output])
    nullval = cp.typer(8, Null, [cp.output])

    def __init__(self):
        self.enm = EchoType.TEST


@cp.model()
@sp.table("localdb", "user")
class Login:

    uid = (cp.string(1, [cp.input], "随便输入一个用户id"), sp.cp.string())
    sid = (cp.string(2, [cp.output]), sp.cp.string())
    raw = (cp.string(3, [cp.input, cp.optional], "sdk返回的数据"), sp.cp.string())
    channel = (cp.string(4, [cp.input, cp.optional], "渠道"), sp.cp.string())


@cp.model([cp.auth])
class User:

    uid = cp.string(1, [cp.output], "当前用户id")


@cp.model()
class LoginSDK:

    raw = cp.string(1, [cp.input], "sdk返回的数据")
    channel = cp.string(2, [cp.input], "渠道")
    user = cp.typer(3, User, [cp.output])
    sid = cp.string(4, [cp.output])


@cp.model()
class LoginVerifySDK:

    sid = cp.string(1, [cp.input])
    user = cp.typer(2, User, [cp.output])


@cp.model([cp.auth])
class Message:

    content = cp.string(1, [cp.output], "消息体")


@cp.model([])
class Upload:

    file = cp.file(1, [cp.input, cp.output], "选择一个图片")
