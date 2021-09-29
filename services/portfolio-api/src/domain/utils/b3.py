import datetime

from dateutil.relativedelta import relativedelta
from pytz import timezone

MARKET_OPEN_HOUR = 10
MARKET_CLOSE_HOUR = 17

B3_TIMEZONE = timezone("America/Sao_Paulo")


def is_b3_market_open() -> bool:
    now = datetime.datetime.now().astimezone(B3_TIMEZONE)
    return now.weekday() < 5 and MARKET_OPEN_HOUR <= now.hour <= MARKET_CLOSE_HOUR


def next_b3_market_opening() -> datetime.datetime:
    now = datetime.datetime.now().astimezone(B3_TIMEZONE)
    next_day = now + relativedelta(days=1)
    while next_day.weekday() > 4:
        next_day = next_day + relativedelta(days=1)
    return next_day.replace(hour=MARKET_OPEN_HOUR, minute=0, second=0)


def seconds_to_b3_market_opening() -> int:
    now = datetime.datetime.now().astimezone(B3_TIMEZONE)
    return int(next_b3_market_opening().timestamp() - now.timestamp())
