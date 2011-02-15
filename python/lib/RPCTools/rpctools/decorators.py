import traceback

def callback(fun):
    def call(self, cb, *arg):
        cb(True, fun(self, *arg))

    call.__name__   = fun.__name__
    call.__doc__    = fun.__doc__
    call.__module__ = fun.__module__
    call.__dict__.update(fun.__dict__)
    return call

class StopIterationValue(StopIteration):
    def __init__(self, value):
        self.value = value
        StopIteration.__init__(self)

def generator(func):
    def call(self, cb, *arg):
        def ret(val):
            raise StopIterationValue(val)

        gen = iter(func(self, ret, *arg))

        try:
            call = gen.next()
        except StopIterationValue, e:
            cb(True, e.value)
        except StopIteration, e:
            cb(True, None)
        except Exception, e:
            cb(False, e)
        else:
            if call.__class__ is tuple:
                fun = call[0]
                args = call[1:]
            else:
                fun = call
                args = ()

            def callback(success, result):
                if success:
                    try:
                        call2 = gen.send(result)
                    except StopIterationValue, e:
                        cb(True, e.value)
                    except StopIteration, e:
                        cb(True, None)
                    except Exception, e:
                        cb(False, traceback.format_exc())
                    else:
                        if call2.__class__ is tuple:
                            fun2 = call2[0]
                            args2 = call2[1:]
                        else:
                            fun2 = call2
                            args2 = ()

                        fun2(callback, *args2)
                else:
                    cb(False, result)

            fun(callback, *args)

    call.__name__   = func.__name__
    call.__doc__    = func.__doc__
    call.__module__ = func.__module__
    call.__dict__.update(func.__dict__)
    return call
