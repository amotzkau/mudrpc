import picklerpc.client, os.path
import pyftpdlib.ftpserver

FIFO="/MUD/rpc/fifo"

class DefaultSite:
    root_dir="/"
    login_msg_file=None
    users_dir=None
    dir_msg=".info"
    validate=True

def get_site(username):
    return DefaultSite

def indent(text):
    """Indent all but the first line of the given text
    so it won't contain an FTP return code."""

    text = text.replace("\r\n","\n")
    if text.endswith("\n"):
        text = text[:-1]
    return text.replace("\n", "\r\n ")

class MUDAuthorizer:
    """Authorizer that forwards all requests to the MUD."""

    def __init__(self):
        self.mudftp = picklerpc.client.synconnect(FIFO, "ftpd", ondemand = True)
        self.mud = picklerpc.client.synconnect(FIFO, "mud", ondemand = True)

    def validate_authentication(self, username, password):
        """Check the password."""
        if not get_site(username).validate:
            return True

        res = self.mud.password(username, password, "ftp")
        if type(res) == int and res > 0:
            return True
        return False

    def has_perm(self, username, perm, path=None):
        """Whether the user has permission over path (an absolute
        pathname of a file or a directory).

        Expected perm argument is one of the following letters:

        Read permissions:
         - "e" = change directory (CWD command)
         - "l" = list files (LIST, NLST, STAT, MLSD, MLST commands)
         - "r" = retrieve file from the server (RETR command)

        Write permissions:
         - "a" = append data to an existing file (AxPPE command)
         - "d" = delete file (DELE command)
         - "f" = rename file or directory from (RNFR command)
         - "t" = rename file or directory to (RNTO command)
         - "m" = create directory (MKD command)
         - "n" = delete directory (RMD command)
        """

        if path is None:
            return False

        site = get_site(username)

        if not path.startswith(site.root_dir):
            return False

        if not site.validate:
            return perm in "elr"

        path = path[len(site.root_dir):]
        if path == "":
            path = "/"
        return self.mudftp.check_permission(username, perm, path) != 0

    def get_perms(self, username):
        """Returns the base permissions of the user.

        Read-only for anonymous, read-write for authenticated users.
        """
        if username == "anonymous":
            return "elr"
        else:
            return "elradfm"

    def get_home_dir(self, username):
        """Returns the root (not home) directory for the given user."""
        return get_site(username).root_dir

    def get_msg_login(self, username):
        msgfile = get_site(username).login_msg_file
        if msgfile is not None and os.path.exists(msgfile):
            f= file(msgfile, "r")
            return indent(f.read())
        return 'Login successful.'

    def get_msg_quit(self, username):
        return "Goodbye."

    def impersonate_user(self, username, password):
        pass

    def terminate_impersonation(self, username):
        pass

class MUDFS(pyftpdlib.ftpserver.AbstractedFS):
    def __init__(self, root, cmd_channel):
        pyftpdlib.ftpserver.AbstractedFS.__init__(self, root, cmd_channel)
        self.site = get_site(cmd_channel.username)
        if self.site.users_dir is not None:
            self._cwd = os.path.join(self.site.users_dir, cmd_channel.username)

    def ftpnorm(self, ftppath):
        if self.site.users_dir is not None:
            if ftppath.startswith("~/") or ftppath == "~":
                ftppath = self.site.users_dir + "/" + self.cmd_channel.username + ftppath[1:]
            elif  ftppath.startswith("~"):
                ftppath = self.site.users_dir + "/" + ftppath[1:]

        return pyftpdlib.ftpserver.AbstractedFS.ftpnorm(self, ftppath)

    def chdir(self, path):
        pyftpdlib.ftpserver.AbstractedFS.chdir(self, path)

        if self.site.dir_msg is not None:
            msgfile = os.path.join(path, self.site.dir_msg)
            if os.path.exists(msgfile):
                f=file(msgfile, "r")
                self.cmd_channel.push("250-%s\r\n" % indent(f.read()) )
