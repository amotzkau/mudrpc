#
# Author:  Alexander Motzkau <Gnomi@UNItopia.de>
# License: GPLv2
#

"""JSON RPC Client functions.

This module exports three functions.

def synconnect(filename, appname): Connect synchronously to the JSON server.
def asynconnect(filename, appname): Connect asynchronously to the JSON server.
def loop(): The event loop needed for asynchronous calls.
"""

import rpcapps.client
import encoding

synconnect = rpcapps.client.WaitingUnixClient(encoding.JSONEncoding())
asynconnect = rpcapps.client.AsyncUnixClient(encoding.JSONEncoding())

from rpcapps.client import loop

synconnect.__doc__ = """synconnect(filename, appname) -> Blocking JSON client via UNIX sockets.

Connects synchronously (i.e. blocking) to a UNIX domain socket at
'filename' and sends all calls as JSON encoded requests to that
socket with 'appname' as the application name.

The close the connection call _close().
"""

asynconnect.__doc__ = """asynconnect(filename, appname) -> Non-Blocking JSON client via UNIX sockets.

Connects asynchronously (i.e. non-blocking) to a UNIX domain socket at
'filename' and sends all calls as JSON encoded requests to that
socket with 'appname' as the application name. All calls require a callback
function as its first argument. The callback function gets the success state
(True or False) as the first and the return value resp. error message as the
second argument.

The close the connection call _close().
"""
