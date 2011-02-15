class Producer:
    CRLF = "\r\n"

    def __init__(self, msg, packetsize = 900, lf = True):
        self.packetsize = 900
        self.msg = msg
        self.started = False
        if not lf:
            self.CRLF = ''

    def more(self):
        if self.msg is None:
            return None
        elif self.started:
            if len(self.msg)+5 > self.packetsize:
                res = "RPCM" + self.msg[:self.packetsize-5] + '$' + self.CRLF
                self.msg = self.msg[self.packetsize-5:]
            else:
                res = "RPCE" + self.msg + '$' + self.CRLF
                self.msg = None
            return res
        else:
            if len(self.msg)+5 > self.packetsize:
                res = "RPCS" + self.msg[:self.packetsize-5] + '$' + self.CRLF
                self.msg = self.msg[self.packetsize-5:]
            else:
                res = "RPCF" + self.msg + '$' + self.CRLF
                self.msg = None
            self.started = True
            return res
