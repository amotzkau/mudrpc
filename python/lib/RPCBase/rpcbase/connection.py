"""Classes for RPC connection handling

The Connection class provides socket handling for server and client
applications. It reads from a socket and passes the data to an RPC handler.

The Client class provides connection handling (automatic connect
and reconnect) for client applications.

Both classes need calls to the loop() function to work.
"""

import asynchat
import asyncore
import time
import traceback
import socket
import errno

class Connection(asynchat.async_chat):
    def __init__(self, handler, conn = None, map = None):
        try:
            asynchat.async_chat.__init__(self, conn=conn, map=map)
        except TypeError, ex:
            asynchat.async_chat.__init__(self)
            asyncore.dispatcher.__init__(self, conn, map)
        self.buffer = ""
        self.set_terminator("\n")
        self.handler = handler
        handler.connection = self

    def collect_incoming_data(self, data):
        self.buffer += data

    def found_terminator(self):
        data = self.buffer
        self.buffer = ""
        self.handler.receive(data)

    def readable(self):
        return True

    def send_message(self, data):
        self.reconnect()
        self.push(data + "\n")

    def socket_closed(self, msg = None):
        self.discard_buffers()
        self.handler.closed(msg)

    def reconnect(self):
        pass

    def handle_error(self):
        self.close()
        self.socket_closed("Closing socket because of error:\n" + traceback.format_exc() + "\nCurrent Stacktrace:\n" + ''.join(traceback.format_stack()))

    def handle_close(self):
        self.close()
        self.socket_closed()

    def handle_connect(self):
        self.handler.connected()

    def recv(self, buffer_size):
        try:
            data = asynchat.async_chat.recv(self, buffer_size)
            return data
        except socket.error, why:
            if why[0] == errno.EWOULDBLOCK:
                return ''
            else:
                raise

class Client(Connection):
    def __init__(self, handler, ondemand = False, map = None):
        self.ondemand = ondemand

        Connection.__init__(self, handler, map=map)

        if ondemand:
            self.reconnecting = time.time() - 1
        else:
            self.reconnecting = None
            self.connect()

    def start_connect(self):
        self.reconnecting = None
        remove_heartbeat(self)

    def reconnect(self):
        if self.reconnecting != None:
            if self.reconnecting < time.time():
                self.connect()
            else:
                set_heartbeat(self)

    def close(self):
        self.reconnecting = None
        remove_heartbeat(self)
        Connection.close(self)

    def socket_closed(self, msg = None):
        self.reconnecting = time.time() + 1
        if not self.ondemand:
            set_heartbeat(self)
        Connection.socket_closed(self, msg)

    def heartbeat(self):
        if self.reconnecting != None and self.reconnecting < time.time():
            self.connect()

heartbeats = []

def set_heartbeat(conn):
    """Add an object to the heartbeat list.

The function heartbeat() will be called in this object each second as long as
loop() runs. If called multiple times the object will only be added once.
"""
    if not conn in heartbeats:
        heartbeats.append(conn)

def remove_heartbeat(conn):
    """Remove an object from the heartbeat list.

Removes an object from the heartbeat list. If the object isn't in the list
nothing happens.
"""
    if conn in heartbeats:
        heartbeats.remove(conn)

def loop(count=None, map=None):
    """The event loop.

This function monitors all registered sockets and handles incoming and
outgoing traffic. It enters a polling loop that terminates after count
passes or all open channels have been closed. The count argument
defaults to None, resulting in the loop terminating only when all
channels have been closed.
"""
    while count == None or count > 0:
        if count != None:
            count -= 1
        if map or (map == None and asyncore.socket_map):
            asyncore.loop(timeout = 1, count=1, map=map)
        elif not heartbeats:
            return False
        else:
            time.sleep(1)

        t = time.time()
        for client in heartbeats[:]:
            client.heartbeat()
    return True
