#
# Author:  Alexander Motzkau <Gnomi@UNItopia.de>
# License: GPLv2
#

"""JSON RPC Server functions.

This module exports two functions.

def register(filename, apps): Register a JSON server for UNIX sockets.
def loop(): The event loop that monitors all sockets.
"""

import rpcapps.server
import encoding

register = rpcapps.server.UnixServer(encoding.JSONEncoding())

from rpcapps.server import loop

register.__doc__ = """register(filename, apps) -> JSON server via UNIX sockets.

Creates a FIFO with 'filename' and listens on it for incoming
connections, where it will answer JSON encoded requests.
'apps' should be a dictionary that maps application names
to callables that return an application object. All requests
will then be translated to calls to this application object
with a callback object as its first parameter and the arguments
from the RPC call as subsequent parameters.
"""
