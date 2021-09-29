import os
from decimal import Decimal
from functools import wraps
from typing import List, Dict, Callable, Optional

from redis import Redis

import domain.utils as utils
from domain.models.intraday_info import IntradayInfo
from goatcommons.cedro.client import CedroMarketDataClient

REDIS = Redis(host=os.getenv("REDIS_HOST"), port=6379, db=0)


def cache_snapshot():
    return {
        key.decode("utf-8"): {
            "value": REDIS.get(key).decode("utf-8"),
            "ttl": REDIS.ttl(key),
        }
        for key in REDIS.scan_iter()
    }


def invalidate_cache():
    REDIS.delete(*[key for key in REDIS.scan_iter()])


def cached_function(expiration_time_fn: Callable[[], int]):
    def wrapper(func):
        @wraps(func)
        def f_wrapper(*args, **kwargs):
            key = args[1]

            cached_value = get_cached_info(key)
            if cached_value:
                return cached_value

            value = func(*args, **kwargs)
            put_cached_info(key, expiration_time_fn(), value)

            return value

        return f_wrapper

    return wrapper


def get_cached_info(key: str) -> Optional[IntradayInfo]:
    cached_value = REDIS.get(key)
    if cached_value:
        return eval(cached_value)


def put_cached_info(key: str, expiration_time: int, info: IntradayInfo):
    REDIS.setex(key, expiration_time, str(info))


def cache_expiration_time() -> int:
    return 300 if utils.is_b3_market_open() else utils.seconds_to_b3_market_opening()


class CedroStockIntradayClient:
    def __init__(self):
        self.cedro = CedroMarketDataClient()
        self.redis = Redis(host=os.getenv("REDIS_HOST"), port=6379, db=0)

    @staticmethod
    def quote_dict_to_intraday_info(quote: dict) -> IntradayInfo:
        return IntradayInfo(
            ticker=quote["symbol"].upper(),
            company_name=quote["company"],
            current_price=Decimal(quote["lastTrade"] or quote["previous"]).quantize(
                Decimal("0.01")
            ),
            yesterday_price=Decimal(quote["previous"]).quantize(Decimal("0.01")),
            today_variation_percentage=Decimal((quote["change"])).quantize(
                Decimal("0.01")
            ),
        )

    @cached_function(expiration_time_fn=cache_expiration_time)
    def get_intraday_info(self, ticker: str) -> IntradayInfo:
        result = self.cedro.quote(ticker)

        return self.quote_dict_to_intraday_info(result)

    @utils.retry(exception_to_check=Exception, tries=3, delay=0.1)
    def batch_get_intraday_info(self, tickers: List[str]) -> Dict[str, IntradayInfo]:
        response = self.get_intraday_info_from_cache(tickers)

        not_in_cache_tickers = set(tickers) - set(response.keys())
        if not_in_cache_tickers:
            quotes = self.cedro.quotes(not_in_cache_tickers)
            for quote in quotes:
                data = self.quote_dict_to_intraday_info(quote)
                put_cached_info(data.ticker, cache_expiration_time(), data)
                response[data.ticker] = data

        return response

    @staticmethod
    def get_intraday_info_from_cache(tickers: List[str]) -> Dict[str, IntradayInfo]:
        response = {}
        for ticker in tickers:
            cached_value = get_cached_info(ticker)
            if cached_value:
                response[ticker] = cached_value
        return response
