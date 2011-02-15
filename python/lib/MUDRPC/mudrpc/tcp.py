import asyncore
import asynchat
import socket
import time
from rpcbase import connection
from producer import Producer

class Connection(connection.Connection):
    def __init__(self, handler, conn = None):
        connection.Connection.__init__(self, handler, conn)
        self.set_terminator("\r\n")

    def send_message(self, data):
        self.reconnect()
        self.push_with_producer(Producer(data))

class Client(connection.Client):
    def __init__(self, port, handler, ondemand = False, map = None):
        self.port = port
        connection.Client.__init__(self, handler, ondemand, map)
        self.set_terminator("\r\n")

    def send_message(self, data):
        self.reconnect()
        self.push_with_producer(Producer(data))

    def connect(self):
        self.start_connect()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("127.0.0.1",0))
        connection.Connection.connect(self, ("127.0.0.1", self.port))

from rpcbase.connection import loop
