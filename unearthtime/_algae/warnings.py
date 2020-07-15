import warnings

class ParameterWarning(UserWarning):
	pass

def overridinguseof(this, with_):
	warnings.warn("Overriding use of %r with %r." % (this, with_), ParameterWarning)