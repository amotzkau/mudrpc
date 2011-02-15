import asyncore
import asynchat
import socket
import time
from rpcbase import connection
from producer import Producer

class Client(connection.Connection):
    def __init__(self, port, handler, map = None):
        self.port = port

        connection.Connection.__init__(self, handler, map=map)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
        sock.setblocking(0)
        self.set_socket(sock)
        self.bind(("127.0.0.1",0));
        self.connect(("127.0.0.1", self.port))
        self.set_terminator(None)
        self.buffer = None

    def send_message(self, data):
        self.reconnect()
        self.push_with_producer(Producer(data, 1024, False))

    def collect_incoming_data(self, data):
        if data[0:3]!='RPC':
            print "Illegal Packet:", data
            return

        if data[3] == 'F':
            self.handler.receive(data[4:])
        elif data[3] == 'S':
            self.buffer = data[4:]
        elif data[3] == 'M':
            if self.buffer == None:
                print "Missing Packet!"
                return
            self.buffer += data[4:]
        elif data[3] == 'E':
            if self.buffer == None:
                print "Missing Packet!"
                return
            msg = self.buffer + data[4:]
            self.buffer = ''
            self.handler.receive(msg)

from rpcbase.connection import loop
