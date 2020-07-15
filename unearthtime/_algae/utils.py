from inspect import signature as sig, _ParameterKind as p_kind
from time import sleep

def arityof(value): return len([p for p in sig(value).parameters.values() if not p.kind in (p_kind.VAR_POSITIONAL, p_kind.VAR_KEYWORD)]) if callable(value) else -1

def displayed(iter): return firstwhere(lambda e: 'display: none' not in e.style, iter)

def isfalse(value): return isinstance(value, bool) and not value

def isnullary(value): return callable(value) and len(sig(value).parameters) == 0

def istrue(value): return isinstance(value, bool) and value

def k_arityof(value): return len([p for p in sig(value).parameters.values() if p.kind in (p_kind.KEYWORD_ONLY, p_kind.POSITIONAL_OR_KEYWORD)])

def p_arityof(value): return len([p for p in sig(value).parameters.values() if p.kind in (p_kind.POSITIONAL_ONLY, p_kind.POSITIONAL_OR_KEYWORD)]) if callable(value) else -1

def raiseif(condition, exception):
    if condition:
        raise exception
	
def until(method, *args, wait=0, cycles=50, **kwargs):
	cycle = 0
	while method(*args, **kwargs) and cycle < cycles:
		if wait:
			sleep(wait)

		cycle += 1

def firstwhere(condition, iterable):
	for i, obj in enumerate(iterable):
		if condition(obj):
			return i, obj
	else:
		return None

def newlambda(name, argcount):
	return "f = lambda driver, %s: driver.execute_script('return timelapse.%s(%s)')" % (
		', '.join(chr(i + 97) for i in range(argcount)),
		name,
		', '.join(chr(i + 97) for i in range(argcount))) if argcount > 0 else "f = lambda driver: driver.execute_script('return timelapse.%s()')" % name