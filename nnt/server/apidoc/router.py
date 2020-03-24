from ...core import proto as cp, router as r, url, kernel
from ...core.python import *
from ...core.models import *
from ..transaction import Transaction
from ..routers import *


class ParameterInfo:

    def __init__(self):
        super().__init__()

        self.name: str = None
        self.string: bool = False
        self.integer: bool = False
        self.double: bool = False
        self.number: bool = False
        self.boolean: bool = False
        self.file: bool = False
        self.intfloat: int = 0
        self.enum: bool = False
        self.array: bool = False
        self.map: bool = False
        self.object: bool = False
        self.optional: bool = False
        self.index:  int = 0
        self.input: bool = False
        self.output: bool = False
        self.comment: str = None
        self.valtyp = None
        self.keytyp = None


class ActionInfo:

    def __init__(self):
        super().__init__()

        self.name: str = None
        self.action: str = None
        self.comment: str = None
        self.params: [ParameterInfo] = None


class RouterConfig:

    class Export:

        def __init__(self):
            super().__init__()
            self.router: [str] = None
            self.model: [str] = None

    def __init__(self):
        super().__init__()
        self.export = Export()


@cp.model
class ExportApis:

    node = cp.boolean(1, [cp.input, cp.optional], "生成 logic.node 使用的api")
    php = cp.boolean(2, [cp.input, cp.optional], "生成 logic.php 使用的api")
    h5g = cp.boolean(3, [cp.input, cp.optional], "生成 game.h5 游戏使用api")
    vue = cp.boolean(4, [cp.input, cp.optional], "生成 vue 项目中使用的api")


class Router(r.IRouter):

    def __init__(self):
        super().__init__()
        self._cfg = None
        self.action = 'api'
        self._page = get_file_content(
            url.expand("~/nnt/server/apidoc/apidoc.volt"))

    @r.action(Null, [r.expose], "文档")
    def doc(self, trans: Transaction):
        srv: IRouterable = trans.server
        if len(srv.routers):
            # 收集routers的信息
            infos = self.ActionsInfo(srv.routers)
            # 渲染页面
            cnt = self._page.replace('{{action}}', kernel.toJson(infos))
            trans.output('text/html;charset=utf-8;', cnt)
            return
        trans.submit()

    def config(self, cfg):
        self._cfg = cfg
        return True

    @staticmethod
    def ActionsInfo(routers: Routers) -> [ActionInfo]:
        t: [ActionInfo] = []
        for e in routers:
            t.append(Router.RouterActions(routers[e]))
        return t

    @staticmethod
    def RouterActions(router: r.IRouter) -> [ActionInfo]:
        name = router.action

        # 获得router身上的action信息以及属性列表
        asnms = r.GetAllActionNames(router)
        acts = []
        for asnm in asnms:
            ap = r.FindAction(router, asnm)
            t = {
                'name': '%s.%s' % (name, asnm),
                'action': '%s.%s' % (name, asnm),
                'comment': ap.comment,
                'params': Router.ParametersInfo(ap.clazz)
            }
            acts.append(t)
        return acts

    @staticmethod
    def ParametersInfo(clz):
        ps = []
        infos = cp.GetAllFields(clz)
        for nm in infos:
            info: cp.FieldOption = infos[nm]
            t = {
                'name': nm,
                'array': info.array,
                'string': info.string,
                'integer': info.integer,
                'double': info.double,
                'number': info.number,
                'intfloat': info.intfloat,
                'boolean': info.boolean,
                'file': info.file,
                'enum': info.enum,
                'array': info.array,
                'map': info.map,
                'object': info.json,
                'optional': info.optional,
                'index': info.id,
                'input': info.input,
                'output': info.output,
                'comment': info.comment,
                'valtyp': info.valtype,
                'keytyp': info.keytype
            }
            ps.append(t)
        return ps
