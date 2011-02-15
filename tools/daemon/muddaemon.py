#! /usr/bin/python
#
# The daemon always keeps a connection into the MUD so
# its function can be called from the MUD.

import os
import rpctools
from rpctools.decorators import callback, generator
import mudrpc.client
import picklerpc.server
import picklerpc.client
import jsonrpc.server
import socket

# An example app:
class App(rpctools.CallbackHelper):
    def __init__(self):
        self.nr = 0
        pass

    def hello(self, text):
        self.nr += 1
        return [ "Echo", text, self.nr ]


# Now we define all the connections.
# All connections offer two-way communication, so the only
# difference between a server and a client class is that
# the client makes the connections a server is waiting for.

# The connection into the MUD, we use port 33033.
daemon = mudrpc.client.tcpconnect(33033,
    # Here we define all the applications that can be
    # called from the MUD.
    { "app":    App,
    },
    # This function is called upon a successfull connection.
    # We call control::register_daemon in the MUD.
    lambda handler: rpctools.RedirectApp("control", handler).register_daemon(rpctools.void))

oldumask = os.umask(007)

# A connection for the ftpd: We relay its requests into the MUD
# so it doesn't have to keep an own connection into it.
picklerpc.server.register("/MUD/rpc/fifo",
    # These two applications can be called in that FIFO (from ftpd).
    { "mud": lambda: rpctools.RedirectApp("mud", daemon),
      "ftpd": lambda: rpctools.RedirectApp("ftpd", daemon)
    })

# Another example for Perl scripts we have a JSON encoded FIFO:
jsonrpc.server.register("/UNItopia/mudadm/python/rpc/news/perl",
    { "mud":  lambda: rpctools.RedirectApp("mud", daemon)
    })

os.umask(oldumask)

try:
    mudrpc.client.loop()
except KeyboardInterrupt:
    pass
