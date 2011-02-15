#! /usr/bin/python

import os

from pyftpdlib import ftpserver
from pyftpdlib.contrib.handlers import TLS_FTPHandler
from OpenSSL import SSL
import mudauthorizer


class UserSite:
    root_dir="/MUD/lib"
    login_msg_file="/static/adm/FTP.MOTD"
    users_dir="/w"
    dir_msg=".info"
    validate=True

class AnonSite:
    root_dir="/MUD/lib/pub"
    login_msg_file="/.message"
    users_dir=None
    dir_msg=".message"
    validate=False

def get_site(username):
    if username == 'anonymous':
        return AnonSite
    else:
        return UserSite

mudauthorizer.get_site = get_site

cmd_perm_overrides = {
    'APPE' : 'a', # Append file
    'CDUP' : 'e', # cd ..
    'CWD'  : 'e', # cd <name>
    'DELE' : 'd', # rm
    'LIST' : 'l', # ls
    'MDTM' : 'l', # get last modification time
    'MLSD' : 'l', # ls
    'MLST' : 'l', # ls
    'MKD'  : 'm', # mkdir
    'NLST' : 'l', # ls
    'RETR' : 'r', # get
    'RMD'  : 'n', # rmdir
    'RNFR' : 'f', # rename from
    'RNTO' : 't', # rename to
    'SIZE' : 'l', # get file size
    'STAT' : 'l', # stat
    'STOR' : 'w', # put
    'STOU' : 'w', # put unique
    'XCUP' : 'e', # cd ..
    'XCWD' : 'e', # cd ..
    'XMKD' : 'm', # mkdir
    'XRMD' : 'n', # rmdir
    }

class FTPHandler(TLS_FTPHandler):
    authorizer = mudauthorizer.MUDAuthorizer()
    abstracted_fs = mudauthorizer.MUDFS
    certfile = "/etc/ssl/certs/ftpd.pem"
    keyfile = "/etc/ssl/private/ftpd.pem"
    banner = "MUD FTPD ready."
    passive_ports = range(35000, 35100)

    def __init__(self, conn, server):
        TLS_FTPHandler.__init__(self, conn, server)
        for (cmd,perm) in cmd_perm_overrides.iteritems():
            self.proto_cmds[cmd]['perm'] = perm

    def on_login(self, username):
        # Increase timeout after successful login.
        if username != 'anonymous':
            self.timeout = 7200

os.umask(027)

def run_ftpd():
    # Instantiate FTP server class and listen to 0.0.0.0:21
    address = ('', 2221)
    ftpd = ftpserver.FTPServer(address, FTPHandler)

    # set a limit for connections
    ftpd.max_cons = 256
    ftpd.max_cons_per_ip = 5

    # start ftp server
    ftpd.serve_forever()

try:
    run_ftpd()
except KeyboardInterrupt:
    pass
