import rpcapps.server
import encoding

register = rpcapps.server.UnixServer(encoding.PickleEncoding())

from rpcapps.server import loop
