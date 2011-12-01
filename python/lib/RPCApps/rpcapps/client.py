from rpcbase.unix import loop

def WaitingUnixClient(encoding):
    from rpcbase.handler import RPCHandler
    from rpcbase.unix import Client
    from rpctools import WaitingClient

    def connect(filename, name, ondemand = False):
        client_map = {}
        handler = RPCHandler(encoding)
        client = Client(filename, handler, ondemand = ondemand, map=client_map)
        return WaitingClient(name, handler, loop, client_map)
    return connect

def AsyncUnixClient(encoding):
    from rpcbase.handler import RPCHandler
    from rpcbase.unix import Client
    from rpctools import RedirectApp

    def connect(filename, name, ondemand = False, map=None):
        handler = RPCHandler(encoding)
        client = Client(filename, handler, ondemand, map=map)
        return RedirectApp(name, handler)
    return connect

