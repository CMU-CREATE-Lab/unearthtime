from functools import wraps

def returnonexception(ret_val, exception: Exception):
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except exception:
                return ret_val
        return wrapper
    return decorator