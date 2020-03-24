from .render import AbstractRender
from ..transaction import *
from ...core.python import *
from ...core.kernel import *
from ...core import proto as cp
from ...core.models import STATUS


class Json(AbstractRender):

    def __init__(self):
        super().__init__()
        self.type = 'application/json'

    def render(self, trans: Transaction, opt: TransactionSubmitOption) -> str:
        r = None
        if opt and opt.model:
            if opt.raw:
                s = toString(trans.model)
                return s
            r = cp.Output(trans.model)
            if trans.model and r == None:
                r = {}
        else:
            r = {
                'code': trans.status
            }
            if trans.status != STATUS.OK:
                r['message'] = trans.message
            else:
                r['data'] = trans.model if (
                    opt and opt.raw) else cp.Output(trans.model)
                if r['data'] == None and trans.model:
                    r['data'] = {}
        cmid = at(trans.params, "_cmid")
        if cmid != None:
            r["_cmid"] = cmid
        listen = at(trans.params, "_listening")
        if listen != None:
            r["_listening"] = listen
        s = toJson(r)
        return s
