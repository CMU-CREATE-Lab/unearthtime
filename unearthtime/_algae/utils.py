from inspect import Parameter, signature as sig
from time import sleep
from typing import Iterable


def arityof(method): return len([param for param in sig(method).parameters.values() if param.kind not in (
    Parameter.VAR_POSITIONAL,
    Parameter.VAR_KEYWORD)]) if callable(method) else -1


def displayed(elements): return firstwhere(lambda element: 'display: none' not in element.style and 'display:none' not in element.style, elements)


def firstwhere(condition, iterable):
    for i, obj in enumerate(iterable):
        if condition(obj):
            return i, obj
    else:
        return None


def isfalse(boolean): return isinstance(boolean, bool) and not boolean


def isint(value): return isinstance(value, int) or hasattr(value, '__index__')


def is_nonstring_iterable(value): return isinstance(value, Iterable) and not isinstance(value, str)


def isnullary(method): return callable(method) and len(sig(method).parameters) == 0


def istrue(boolean): return isinstance(boolean, bool) and boolean


def k_arityof(method): return len([param for param in sig(method).parameters.values() if param.kind in (
    Parameter.KEYWORD_ONLY,
    Parameter.POSITIONAL_OR_KEYWORD)]) if callable(method) else -1


def newlambda(cls, name, argcount):
    if argcount > 0:
        args = ', '.join(chr(i + 97) for i in range(argcount))
        lamb = f"f = lambda driver, {args}: driver.execute_script(f'return {cls}.{name}({', '.join([f'{{{arg}}}' for arg in args.split(', ')])})')"
    else:
        lamb = f"f = lambda driver: driver.execute_script('return {cls}.{name}()')"

    return lamb


def p_arityof(method): return len([param for param in sig(method).parameters.values() if param.kind in (
    Parameter.POSITIONAL_ONLY,
    Parameter.POSITIONAL_OR_KEYWORD)]) if callable(method) else -1


def raiseif(condition, exception):
    if condition:
        raise exception


def until(method, *args, wait=0, cycles=50, **kwargs):
    cycle = 0
    while not method(*args, **kwargs) and cycle < cycles:
        if wait:
            sleep(wait)

        cycle += 1


def where(condition, iterable): return list(filter(condition, iterable))
