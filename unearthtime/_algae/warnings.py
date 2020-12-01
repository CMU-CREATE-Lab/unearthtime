import warnings


class ParameterWarning(UserWarning):
    pass


def overriding(this): warnings.warn(f'Overriding use of {this!r}.', ParameterWarning)

def overridinginvalidinput(this, with_): warnings.warn(f'Using default value {this!r} over invalid input {with_!r}.', ParameterWarning)


def overridinguseof(this, with_): warnings.warn(f"Overriding use of {this!r} with {with_!r}.", ParameterWarning)
