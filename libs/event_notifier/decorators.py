import time
import traceback
from functools import wraps
from .client import ShitNotifierClient
import traceback


def notify(message: str, notify_level: str):
    def deco_notify(f):
        @wraps(f)
        def f_notify(*args, **kwargs):
            result = f(*args, **kwargs)
            try:
                f_message = message
                if isinstance(result, tuple):
                    f_message = message.format(*result)
                elif result:
                    f_message = message.format(result)

                ShitNotifierClient().send(
                    notify_level,
                    "corporate-events.download_today_corporate_events_handler",
                    f_message,
                )
            except Exception as e:
                print(str(e))
                raise e

            return result

        return f_notify

    return deco_notify


def notify_exception(exception_to_check, notify_level: str):
    def deco_notify(f):
        @wraps(f)
        def f_notify(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exception_to_check as e:
                ShitNotifierClient().send(
                    notify_level,
                    f"{f.__module__}.{f.__name__}",
                    traceback.format_exc(),
                )
                raise e

        return f_notify

    return deco_notify
