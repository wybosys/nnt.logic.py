from nnt.server.transaction import Transaction

class Trans(Transaction):

    def __init__(self):
        super().__init__()
        self.uid = None
        self.sid = None

    async def collect(self):
        #this.sid = this.params['_sid'];
        #let fnd = await Get(Login, {sid: this.sid});
        #if (fnd) {
        #    this.uid = fnd.uid;        
        pass

    def auth(self):
        return self.uid != None and self.sid != None    

    def userIdentifier(self):
        return self.uid    

    def sessionId(self):
        return self.sid
