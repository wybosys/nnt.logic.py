import japronto


class JaprontoNonblockingApplication(japronto.Application):

    def _run(self, *, host, port, worker_num=None, reloader_pid=None, debug=None):
        self._debug = debug or self._debug
        if self._debug and not self._log_request:
            self._log_request = self._debug

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        os.set_inheritable(sock.fileno(), True)

        self.workers = set()
        for _ in range(worker_num or 1):
            worker = multiprocessing.Process(
                target=self.serve,
                kwargs=dict(sock=sock, host=host, port=port,
                            reloader_pid=reloader_pid))
            worker.daemon = True
            worker.start()
            self.workers.add(worker)

        # prevent further operations on socket in parent
        sock.close()

    def wait_all(self):
        for worker in self.workers:
            worker.join()
        self.workers.clear()

    def stop_all(self):
        for worker in self.workers:
            worker.terminate()


class JaprontoResponse:

    def __init__(self, req):
        super().__init__()
        self._req = req
        self._headers = {}
        self.code = 200
        self.body = None
        self.raw = None
        self.mime = None
        self._f = futures.Future()
        self._obj = None

    def setHeader(self, k, v):
        if k == 'Content-Type':
            self.mime = v
        else:
            self._headers[k] = v

    def setHeaders(self, d):
        for k in d:
            self.setHeader(k, d[k])

    def send(self):
        # print([self.body, self.raw, self.code, self._headers])
        self._obj = self._req.Response(
            code=self.code,
            headers=self._headers,
            mime_type=self.mime,
            text=self.body,
            body=self.raw
        )
        self._f.set_result(self._obj)

    @property
    def promise(self):
        # 如果已经计算完成，则直接返回response对象，而不是像js返回done之后的promise对象（py看起来不支持）
        if self._obj:
            return self._obj
        return self._f


class HttpServer:

    def __init__(self, rest: Rest):
        super().__init__()
        self._hdl = JaprontoNonblockingApplication()
        self._rest = rest

        async def worker(req):
            return await self._dowork(req)

        # 根目录
        route = '/'
        self._hdl.router.add_route(route, worker)

        # 动态增加目录监听
        n = 0
        while n < 128:
            n += 1
            route += '{_p%d}/' % n
            self._hdl.router.add_route(route, worker)

    async def start(self):
        worker_num = multiprocessing.cpu_count() * 2 if config.DEVOPS else 1
        self._hdl.run(host=self._rest.listen, port=self._rest.port,
                      worker_num=worker_num)
        return True

    def wait(self):
        self._hdl.wait_all()

    def stop(self):
        self._hdl.stop_all()

    async def _dowork(self, req):
        rsp = JaprontoResponse(req)

        # 打开跨域支持
        rsp.setHeader("Access-Control-Allow-Origin", "*")
        rsp.setHeader("Access-Control-Allow-Credentials", "true")
        rsp.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        # 直接对option进行成功响应
        if req.method == "OPTIONS":
            if at(req.headers, "Access-Control-Request-Headers"):
                rsp.setHeader("Access-Control-Allow-Headers",
                              req.headers["Access-Control-Request-Headers"])
            if at(req.headers, "Access-Control-Request-Method") == "POST":
                rsp.setHeader("Content-Type", "multipart/form-data")
            rsp.code = 204
            rsp.send()
            return rsp.promise

        # 处理url请求
        url: str = req.path
        # logger.log(req.path)

        # 支持几种不同的路由格式
        # ?action=xxx.yyy&params
        # $$/xxx.yyy$params
        # xxx/yyy&params
        params = req.query.copy()
        # 为了支持第三方平台通过action同名传递动作
        if url.startswith("/$$/") or url.startswith("/action/"):
            p = url.split("/")
            pl = len(p)
            i = 0
            while i < pl:
                k = p[i]
                v = p[i + 1]
                params[k] = v
                i += 2
        else:
            p = StringT.Split(url, '/')
            pl = len(p)
            if pl >= 2:
                r = p[pl - 2]
                a = p[pl - 1]
                params['action'] = r + '.' + a

        # 如果是post请求，则处理一下form数据
        if req.method == "POST":
            # 如果是multipart-form得请求，则不适用于处理buffer
            ct = at(req.headers, "Content-Type")
            if not ct:
                ct = 'application/json'
            if 'form' in ct:
                form = req.form
                files = req.files
                for k in form:
                    params[k] = form[k]
                for k in files:
                    params[k] = files[k]
            else:
                json = req.json
                for k in json:
                    params[k] = json[k]

        await self.invoke(params, req, rsp)
        return rsp.promise

    async def invoke(self, params, req, rsp: JaprontoResponse, ac=None):
        action = at(params, "action")
        if not action:
            rsp.code = 400
            rsp.send()
            return

        t = self._rest.instanceTransaction()
        try:
            t.ace = ac
            t.server = self._rest
            t.action = action
            t.params = params

            # 整理数据
            if req:  # 如果是通过console调用，则req会为none
                if "_agent" in params:
                    t.info.ua = params["_agent"]
                else:
                    t.info.ua = at(req.headers, 'User-Agent')
                if not t.info.ua:
                    t.info.ua = 'unknown'
                t.info.agent = t.info.ua.lower()
                t.info.host = at(req.headers, 'Host')
                t.info.origin = at(req.headers, 'Origin')
                t.info.referer = at(req.headers, 'Referer')
                t.info.path = req.path
                if 'Accept-Encoding' in req.headers:
                    t.gzip = 'gzip' in req.headers['Accept-Encoding']

                # 获取客户端真实ip
                if not t.info.addr:  # docker
                    t.info.addr = at(req.headers, 'Http_X_Forwarded_For')
                if not t.info.addr:  # proxy
                    t.info.addr = at(req.headers, 'X-Forwarded-For')
                if not t.info.addr:  # normal
                    t.info.addr = req.remote_addr

            # 绑定解析器
            # _pfmt parser format 预留关键字
            t.parser = FindParser(at(params, '_pfmt'))
            # _ofmt render format 预留关键字
            t.render = FindRender(at(params, '_rfmt'))

            # 处理调用
            self._rest.onBeforeInvoke(t)
            await self._rest.doInvoke(t, params, req, rsp, ac)
            self._rest.onAfterInvoke(t)
        except Exception as err:
            logger.exception(err)
            t.status = STATUS.EXCEPTION
            t.submit()

        # 清理事物
        t.clear()

    def submit(self, t: Transaction, opt: TransactionSubmitOption = None):
        pl: TransactionPayload = t.payload
        ct = {
            "Content-Type": opt.type if (opt and opt.type) else t.render.type
        }
        if t.gzip:
            ct["Content-Encoding"] = "gzip"
        if t.responseSessionId:
            ct[RESPONSE_SID] = t.responseSessionId
        buf = t.render.render(t, opt)
        if t.gzip:
            pl.rsp.raw = codec.gzip_compress(buf)
        else:
            pl.rsp.body = buf
        pl.rsp.setHeaders(ct)
        pl.rsp.send()

    def output(self, t: Transaction, typ: str, obj):
        pl: TransactionPayload = t.payload
        ct = {"Content-Type": typ}
        if t.gzip:
            ct["Content-Encoding"] = "gzip"
        if isinstance(obj, RespFile):
            if obj.cachable:
                # 只有文件对象才可以增加过期控制
                if pl.req.headers["If-Modified-Since"]:
                    # 判断下请求的文件有没有改变
                    if obj.stat.mtime.toUTCString() == pl.req.headers["If-Modified-Since"]:
                        pl.rsp.code = 304
                        pl.rsp.body = 'Not Modified'
                        pl.rsp.send()
                        return
                ct["Expires"] = obj.expire.toUTCString()
                ct["Cache-Control"] = "max-age=" + time.WEEK
                ct["Last-Modified"] = obj.stat.mtime.toUTCString()
            # 如果是提供下载
            if obj.download:
                ct['Accept-Ranges'] = 'bytes'
                ct['Content-Disposition'] = 'attachment; filename=' + obj.file
                ct['Content-Description'] = "File Transfer"
                ct['Content-Transfer-Encoding'] = 'binary'
            if t.gzip and not t.compressed:
                obj = codec.gzip_compress(obj.buffer)
            else:
                obj = obj.buffer
            pl.rsp.raw = obj
            pl.rsp.setHeaders(ct)
            pl.rsp.send()
        else:
            if t.gzip and not t.compressed:
                obj = codec.gzip_compress(obj)
            elif type(obj) == str:
                obj = obj.encode('utf-8')
            pl.rsp.raw = obj
            pl.rsp.setHeaders(ct)
            pl.rsp.send()
