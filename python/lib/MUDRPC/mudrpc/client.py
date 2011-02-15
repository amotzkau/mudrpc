import rpcbase.handler
import tcp
import udp
import rpctools
import encoding

from tcp import loop

def syntcpconnect(port, name, apps = {}, connecthandler = None):
    client_map = {}
    handler = rpcbase.handler.RPCHandler(encoding.LPCEncoding(), apps, connecthandler)
    client = tcp.Client(port, handler, True, map=client_map)
    return rpctools.WaitingClient(name, handler, loop, client_map)

def synudpconnect(port, name, apps = {}, connecthandler = None):
    client_map = {}
    handler = rpcbase.handler.RPCHandler(encoding.LPCEncoding(), apps, connecthandler)
    client = udp.Client(port, handler, map=client_map)
    return rpctools.WaitingClient(name, handler, loop, client_map)

def asyntcpconnect(port, name, apps = {}, connecthandler = None):
    handler = rpcbase.handler.RPCHandler(encoding.LPCEncoding(), apps, connecthandler)
    client = tcp.Client(port, handler)
    return rpctools.RedirectApp(name, handler)

def asynudpconnect(port, name, apps = {}, connecthandler = None):
    handler = rpcbase.handler.RPCHandler(encoding.LPCEncoding(), apps, connecthandler)
    client = udp.Client(port, handler)
    return rpctools.RedirectApp(name, handler)

def tcpconnect(port, apps = {}, connecthandler = None):
    handler = rpcbase.handler.RPCHandler(encoding.LPCEncoding(), apps, connecthandler)
    client = tcp.Client(port, handler)
    return handler

def udpconnect(port, apps = {}, connecthandler = None):
    handler = rpcbase.handler.RPCHandler(encoding.LPCEncoding(), apps, connecthandler)
    client = udp.Client(port, handler)
    return handler
