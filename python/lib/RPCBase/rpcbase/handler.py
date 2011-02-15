import traceback
import time
from defs import RPCFail, RPCAnswer, RPCRequest

class RPCHandler:
    def __init__(self, encoding, apps = {}, connecthandler = None):
        self.encoding = encoding
        self.apps = apps
        self.loaded_apps = {}
        self.connecter = connecthandler

        self.reqs = {}
        self.counter = 0
        self.prefix = str(time.time())

    def receive(self, msg):
        data = self.encoding.decode(msg)
        if data[0] == RPCAnswer:
            if data[1] in self.reqs:
                cb = self.reqs[data[1]]
                del(self.reqs[data[1]])
                cb(True, data[2])
        elif data[0] == RPCFail:
            if data[1] in self.reqs:
                cb = self.reqs[data[1]]
                del(self.reqs[data[1]])
                cb(False, data[2])
        elif data[0] == RPCRequest:
            if data[2] in self.loaded_apps:
                app = self.loaded_apps[data[2]]
            elif data[2] in self.apps:
                try:
                    app = self.apps[data[2]]()
                except Exception, ex:
                    traceback.print_exc()
                    self.connection.send_message(self.encoding.encode([RPCFail, data[1], traceback.format_exc() ]))
                    return
                self.loaded_apps[data[2]] = app
            else:
                app = None

            cb = lambda success, res: self.connection.send_message(self.encoding.encode([success and RPCAnswer or RPCFail, data[1], res]))

            try:
                if app is None:
                    raise RuntimeError("Application '%s' not found." % (data[2]))
                getattr(app, data[3])(cb, *data[4:])
            except Exception, ex:
                traceback.print_exc()
                self.connection.send_message(self.encoding.encode([RPCFail, data[1], traceback.format_exc() ]))

    def call(self, cb, val):
        self.counter += 1
        callid = "%s#%s" % (self.prefix, self.counter)
        self.reqs[callid] = cb
        self.connection.send_message(self.encoding.encode([ RPCRequest, callid ] + val ))

    def closed(self, msg = None):
        oldreqs = self.reqs
        self.reqs = {}
        for key, cb in oldreqs.iteritems():
            cb(False, msg or "Connection closed unexpectedly.")
        for appname, app in self.loaded_apps.iteritems():
            if hasattr(app, "_closed"):
               app._closed()

    def connected(self):
        if not self.connecter is None:
            self.connecter(self)

    def close(self):
        self.connection.close()

def RPCHandlerCreator(encoding, apps = {}):
    def create(addr):
        return RPCHandler(encoding, apps)
    return create
