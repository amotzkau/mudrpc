
def UnixServer(encoding):
    from rpcbase.handler import RPCHandlerCreator
    from rpcbase.unix import Server
    from rpctools import WaitingClient

    def register(filename, apps):
        handler = RPCHandlerCreator(encoding, apps)
        server = Server(filename, handler)
    return register

from rpcbase.unix import loop
