from ashes import AshesEnv

from ..file import RespFile
from ..routers import *
from ...core import router as r, url, kernel, devops, app, proto as cp


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
        self.index: int = 0
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

    def __init__(self):
        super().__init__()
        self.export = {
            'router': None,
            'model': None
        }


@cp.model()
class ExportApis:
    node = cp.boolean(1, [cp.input, cp.optional], "生成 logic.node 使用的api")
    php = cp.boolean(2, [cp.input, cp.optional], "生成 logic.php 使用的api")
    h5g = cp.boolean(3, [cp.input, cp.optional], "生成 game.h5 游戏使用api")
    vue = cp.boolean(4, [cp.input, cp.optional], "生成 vue 项目中使用的api")


# 预先准备渲染模板
DIR_TEMPLATES = os.path.dirname(__file__)
TEMPLATES = AshesEnv([DIR_TEMPLATES])


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
            cnt = self._page.replace('{{actions}}', kernel.toJson(infos))
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
            t.extend(Router.RouterActions(routers[e]))
        return t

    @staticmethod
    def RouterActions(router: r.IRouter) -> [ActionInfo]:
        name = router.action

        # 获得router身上的action信息以及属性列表
        asnms = r.GetAllActionNames(router.__class__)
        acts = []
        for asnm in asnms:
            ap = r.FindAction(router.__class__, asnm)
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
                'map': info.map,
                'object': info.json,
                'optional': info.optional,
                'index': info.id,
                'input': info.input,
                'output': info.output,
                'comment': info.comment,
                'valtyp': obj_get_classname(info.valtype),
                'keytyp': obj_get_classname(info.keytype)
            }
            ps.append(t)
        return ps

    @r.action(ExportApis, [r.expose], "生成api接口文件")
    def export(self, trans: Transaction):
        m: ExportApis = trans.model
        if not m.node and \
                not m.php and \
                not m.h5g and \
                not m.vue:
            trans.status = STATUS.PARAMETER_NOT_MATCH
            trans.submit()
            return

        # 分析出的所有结构
        params = {
            'domain': devops.GetDomain(),
            'namespace': '',
            'clazzes': [],
            'enums': [],
            'consts': [],
            'routers': []
        }

        if m.php:
            sp = params['domain'].split('/')
            params['namespace'] = sp[0].capitalize() + '\\' + sp[1].capitalize()

        for each in ats(self._cfg, ['export', 'model'], []):
            modu = app.App.shared().requireModule(each)
            for ec in inspect.getmembers(modu, inspect.isclass):
                name, clz = ec
                if not cp.IsModel(clz):
                    # logger.log("跳过生成 %s" % name)
                    continue

                mp = cp.GetModelInfo(clz)
                if mp.hidden:
                    continue
                if mp.enum:
                    em = {
                        'name': name,
                        'defs': []
                    }
                    params['enums'].append(em)
                    # 枚举得每一项定义都是静态的，所以可以直接遍历
                    for each in inspect.getmembers(clz):
                        k, v = each
                        if not k.startswith('_'):
                            em['defs'].append({
                                'name': k,
                                'value': v
                            })
                elif mp.constant:
                    for each in inspect.getmembers(clz):
                        k, v = each
                        params['consts'].append({
                            'name': name.capitalize() + "_" + k.capitalize(),
                            'value': cp.Output(v)
                        })
                else:
                    # 判断是否有父类
                    clazz = {
                        'name': name,
                        'super': mp.parent.__name__ if mp.parent else "ApiModel",
                        'fields': []
                    }
                    params['clazzes'].append(clazz)
                    # 构造临时对象来获得fields得信息
                    fps = cp.GetAllOwnFields(clz)
                    for key in fps:
                        fp = fps[key]
                        if fp.id <= 0:
                            logger.warn("Model的 Field 不能 <=0 %s" % (name + "." + key))
                            continue
                        if not fp.input and not fp.output:
                            continue
                        typ = cp.FpToTypeDef(fp)
                        deco = None
                        if m.php:
                            deco = cp.FpToDecoDefPHP(fp)
                        else:
                            deco = cp.FpToDecoDef(fp, "Model.")
                        clazz['fields'].append({
                            'name': key,
                            'type': typ,
                            'optional': fp.optional,
                            'file': fp.file,
                            'enum': fp.enum,
                            'input': fp.input,
                            'deco': deco
                        })

            # 遍历所有接口，生成接口段
            for e in ats(self._cfg, ['export', 'router'], []):
                modu = app.App.shared().requireModule(e)
                for ec in inspect.getmembers(modu, inspect.isclass):
                    nm, clz = ec
                    if type(clz) != type:
                        continue
                    ass = r.GetAllActions(clz)
                    if not ass:
                        # logger.log('跳过生成接口 %s' % nm)
                        continue
                    router = clz()
                    for name in ass:
                        ap: r.ActionProto = ass[name]
                        d = {}
                        d['name'] = router.action.capitalize() + name.capitalize()
                        d['action'] = router.action + "." + name
                        cn = ap.clazz.__name__
                        if m.vue or m.node:
                            d['type'] = cn
                        elif m.php:
                            d['type'] = 'M' + cn
                        else:
                            d['type'] = "models." + cn
                        d['comment'] = ap.comment
                        params['routers'].append(d)

            # 渲染模板
            tpl = 'apis.dust'
            if m.node:
                tpl = "apis-node.dust"
            elif m.h5g:
                tpl = "apis-h5g.dust"
            elif m.vue:
                tpl = "apis-vue.dust"
            elif m.php:
                tpl = "apis-php.dust"
            out = TEMPLATES.render(tpl, params)
            # 需要加上php的头
            if m.php:
                out = "<?php\n" + out
            apifile = params['domain'].replace('/', '-') + '-apis'
            if m.php:
                apifile += ".php"
            else:
                apifile += ".ts"
            # 输出到客户端
            trans.output('text/plain', RespFile.Plain(out).asDownload(apifile))
