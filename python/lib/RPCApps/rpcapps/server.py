
def UnixServer(encoding):
    from rpcbase.handler import RPCHandlerCreator
    from rpcbase.unix import Server
    from rpctools import WaitingClient

    def register(filename, apps, map = None):
        handler = RPCHandlerCreator(encoding, apps)
        server = Server(filename, handler, map = map)
    return register

from rpcbase.unix import loop
