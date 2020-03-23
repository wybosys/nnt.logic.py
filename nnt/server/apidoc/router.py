from ...core import proto as cp, router as r, url
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
        self.params: list[ParameterInfo] = None


class RouterConfig:

    class Export:

        def __init__(self):
            super().__init__()
            self.router: list[str] = None
            self.model: list[str] = None

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
        self._page = get_file_content(url.expand("~/nnt/server/apidoc/apidoc.volt"))

    @cp.action(Null, [cp.expose], "文档")
    def doc(self, trans: Transaction):
        srv:IRouterable = trans.server
        if len(srv.routers):
            # 收集routers的信息
            infos = r.ActionsInfo(srv.routers)
            # 渲染页面
            trans.output('text/html;charset=utf-8;', this._page.render({actions: toJson(infos)}))
            return
        trans.submit()    

    def config(self, cfg):
        self._cfg = cfg        
        return True

    @staticmethod
    def ActionsInfo(routers: Routers)-> list[ActionInfo]:
        r: list[ActionInfo] = []
        for e in routers:
            r.append(Router.RouterActions(routers[e]))
        return r    

    @staticmethod
    def RouterActions(router: IRouter)-> list[ActionInfo]:
        name = router.action

        # 获得router身上的action信息以及属性列表
        asnms = r.GetAllActionNames(router)
        r = ArrayT.Convert(as, a => {
            let ap = FindAction(router, a);
            let t = JsonObject<ActionInfo>();
            t.name = t.action = name + '.' + a;
            t.comment = ap.comment;
            t.params = this.ParametersInfo(ap.clazz);
            return t;
        });
        this._ActionInfos.set(name, r);
        return r;
    }

    static ParametersInfo(clz: AnyClass): ParameterInfo[] {
        let t = new clz();
        let fps = GetAllFields(t);
        return ObjectT.Convert(fps, (fp, name) => {
            let t = JsonObject<ParameterInfo>();
            t.name = name;
            t.array = fp.array;
            t.string = fp.string;
            t.integer = fp.integer;
            t.double = fp.double;
            t.number = fp.number;
            t.intfloat = fp.intfloat;
            t.boolean = fp.boolean;
            t.file = fp.file;
            t.enum = fp.enum;
            t.array = fp.array;
            t.map = fp.map;
            t.object = fp.json;
            t.optional = fp.optional;
            t.index = fp.id;
            t.input = fp.input;
            t.output = fp.output;
            t.comment = fp.comment;
            t.valtyp = fp.valtype;
            t.keytyp = fp.keytype;
            return t;
        });
    }
}
