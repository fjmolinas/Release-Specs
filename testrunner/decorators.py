import pexpect

def test(func):
    func.__dict__["__test__"] = True
    return func

def task(action):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print("\t{}...".format(action), flush=True, end="")
            try:
                val = func(*args,**kwargs)
            except pexpect.TIMEOUT as e:
                print("TIMEOUT")
                raise pexpect.exceptions.TIMEOUT(e.value)
            except Exception as e:
                print("ERROR")
                raise e
            print("ok")
            return val
        return wrapper
    return decorator

