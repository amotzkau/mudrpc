import asyncore
import asynchat
import socket
import os
import time
import traceback
import connection

class Server(asyncore.dispatcher):
    def __init__ (self, name, handlercreator):
        self.name = name
        self.handlercreator = handlercreator
        asyncore.dispatcher.__init__ (self)

        if os.access(name,os.F_OK):
            os.remove(name)

        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(name)
        self.listen(1024)
 
    def writable(self):
        return False

    def handle_accept(self):
        conn, addr = self.accept()
        connection.Connection(self.handlercreator(addr), conn)

class Client(connection.Client):
    def __init__(self, name, handler, ondemand = False, map = None):
        self.name = name
        connection.Client.__init__(self, handler, ondemand, map)

    def connect(self):
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.start_connect()
        connection.Connection.connect(self, self.name)

from connection import loop
