import time
from functools import wraps
from .client import ShitNotifierClient


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

            return result

        return f_notify

    return deco_notify
