import inspect
import typing
from contextlib import suppress
from functools import wraps


def enforce_types(_callable):
    spec = inspect.getfullargspec(_callable)

    def check_types(*args, **kwargs):
        parameters = dict(zip(spec.args, args))
        parameters.update(kwargs)
        for name, value in parameters.items():
            with suppress(KeyError):
                type_hint = spec.annotations[name]
                if isinstance(type_hint, typing._SpecialForm):
                    continue
                try:
                    actual_type = type_hint.__origin__
                except AttributeError:
                    actual_type = type_hint

                if isinstance(actual_type, typing._SpecialForm):
                    actual_type = typing.get_origin(type_hint) or type_hint

                if not isinstance(value, actual_type):
                    raise TypeError('Unexpected type for \'{}\' (expected {} but found {})'.format(name, type_hint,
                                                                                                   type(value)))

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_types(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    if inspect.isclass(_callable):
        _callable.__init__ = decorate(_callable.__init__)
        return _callable

    return decorate(_callable)
