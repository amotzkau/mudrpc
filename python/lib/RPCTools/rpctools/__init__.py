from rpcbase.defs import RPCFail, RPCAnswer, RPCRequest

class RPCException(Exception):
    "The proxy classes encapsulate errors within such an exception."
    def __init__(self, val):
        self.value = val

    def __str__(self):
        if self.value.__class__ == str:
            return self.value
        else:
            return repr(self.value)

    def __reduce__(self):
        return (RPCException, (self.value,))


class RedirectApp:
    "This is an application that redirects all calls to another channel."
    def __init__(self, name, channel):
        self._channel = channel
        self._name = name

    def __getattr__(self, fun):
        if not fun.startswith("_"):
            def call(cb, *arg):
                val = [self._name, fun]
                val.extend(arg)
                self._channel.call(cb, val)
            return call
        else:
            raise AttributeError, fun

    def _close(self):
        self._channel.close()

class CallbackHelper(object):
    """An application can inherit this class to get rid of the callback
       parameter. Its functions must return at once and are not allowed
       to call other RPC channels."""
    def __getattribute__(self, name):
        fun = object.__getattribute__(self, name)
        if name.startswith("_") or not hasattr(fun, "__call__"):
            return fun

        def call(cb, *arg):
            cb(True, fun(*arg))
        return call

class CallbackRedirectApp:
    """This application redirects all calls to another class without
    the callback parameter. Its function must return at once and are
    not allowed to call other RPC channels."""

    def __init__(self, app):
        self.app = app

    def __getattr__(self, fun):
        if not fun.startswith("_"):
            def call(cb, *arg):
                cb(True, self.app.__getattr__(fun)(*arg))
            return call
        else:
            raise AttributeError, fun

class WaitingClient:
    """This is for clients only. It will wait for an answer."""

    def __init__(self, name, channel, loop, map = None):
        self._name = name
        self._channel = channel
        self._loop = loop
        self._map = map

    def __getattr__(self, fun):
        if not fun.startswith("_"):
            def call(*arg):
                from asyncore import loop
                val = [self._name, fun]
                val.extend(arg)

                result = [None, None]

                def cb(success, res):
                    result[0] = success
                    result[1] = res

                self._channel.call(cb, val)
                while result[0] == None and self._loop(count = 1, map = self._map):
                    pass

                if result[0] == None:
                    raise RPCException("Connection closed unexpectedly.")
                elif result[0]:
                    return result[1]
                elif result[1].__class__ == RPCException:
                    raise result[1]
                else:
                    raise RPCException(result[1])
            return call
        else:
            raise AttributeError, fun

    def _close(self):
        self._channel.close()

def void(success, val):
    pass
