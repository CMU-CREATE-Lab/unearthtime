import warnings


class ParameterWarning(UserWarning):
    pass


def overridinginvalidinput(this, with_): warnings.warn('Using default value %r over invalid input %r.' % (this, with_), ParameterWarning)


def overridinguseof(this, with_): warnings.warn("Overriding use of %r with %r." % (this, with_), ParameterWarning)
