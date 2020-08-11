from __future__ import annotations

from functools import wraps
from typing import Tuple, Union


def returnonexception(ret, exc: Union[Exception, Tuple[Exception]]):
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except exc:
                return ret

        return wrapper

    return decorator
