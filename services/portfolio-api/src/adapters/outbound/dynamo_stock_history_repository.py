import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from functools import wraps
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from dateutil.relativedelta import relativedelta
from redis import Redis

from domain.models.performance import CandleData
from goatcommons.cedro.client import CedroMarketDataClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class DynamoStockHistoryRepository:
    DATE_FORMAT = "%Y%m01"

    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("MarketData")
        self.__client = boto3.client("dynamodb")

    def find_by_ticker_and_date(
        self, ticker: str, _date: datetime.date
    ) -> Optional[CandleData]:
        result = self.__table.query(
            KeyConditionExpression=Key("ticker").eq(ticker)
            & Key("candle_date").eq(_date.strftime(self.DATE_FORMAT))
        )
        if result["Items"]:
            return CandleData(**result["Items"][0])

    def find_by_ticker_from_date(
        self, ticker: str, _date: datetime.date
    ) -> Optional[List[CandleData]]:
        result = self.__table.query(
            KeyConditionExpression=Key("ticker").eq(ticker)
            & Key("candle_date").gte(_date.strftime(self.DATE_FORMAT))
        )
        if result["Items"]:
            return [CandleData(**data) for data in result["Items"]]
        return []

    def find_by_tickers_and_date(
        self, tickers: List[str], _date: datetime.date
    ) -> Optional[List[CandleData]]:
        response = self.__client.batch_get_item(
            RequestItems={
                "MarketData": {
                    "Keys": [
                        {
                            "ticker": {"S": ticker},
                            "candle_date": {"S": _date.strftime(self.DATE_FORMAT)},
                        }
                        for ticker in set(tickers)
                    ],
                    "ConsistentRead": False,
                }
            },
            ReturnConsumedCapacity="NONE",
        )
        candles = []
        deserializer = TypeDeserializer()
        for data in response["Responses"]["MarketData"]:
            candles.append(CandleData(**deserializer.deserialize({"M": data})))
        return candles


class RedisMarketData:
    redis = Redis(host=os.getenv("REDIS_HOST"), port=6379, db=0)

    def get_intraday_data(self, key):
        try:
            result = self.redis.get(key.upper())
            if result:
                logger.info(f"{key} in cache, returning.")
                return eval(result)
        except Exception as e:
            logger.exception("CAUGHT EXCEPTION getting key from redis: ", e)

    def put_intraday_data(self, ticker, data):
        try:
            self.redis.setex(
                ticker.upper(), self.calculate_expiration_time(), str(data)
            )
        except Exception as e:
            logger.exception("CAUGHT EXCEPTION putting key from redis: ", e)

    @staticmethod
    def is_market_open(now):
        return now.weekday() < 5 and 12 <= now.hour <= 21

    @staticmethod
    def next_market_opening(now):
        next_day = now + relativedelta(days=1)
        while next_day.weekday() > 4:
            next_day = next_day + relativedelta(days=1)
        return next_day.replace(hour=12, minute=0, second=0)

    @staticmethod
    def calculate_expiration_time():
        now = datetime.now(tz=timezone.utc)
        if RedisMarketData.is_market_open(now):
            return 300
        next_opening = RedisMarketData.next_market_opening(now)
        return int(next_opening.timestamp() - now.timestamp())

    @staticmethod
    def cached_tuple(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = args[1]
            result = None

            try:
                result = RedisMarketData.redis.get(key)
            except Exception as e:
                logger.exception("CAUGHT EXCEPTION getting key from redis: ", e)

            if result is None:
                value = func(*args, **kwargs)
                try:
                    RedisMarketData.redis.setex(
                        key, RedisMarketData.calculate_expiration_time(), str(value)
                    )
                except Exception as e:
                    logger.exception("CAUGHT EXCEPTION putting key from redis: ", e)
            else:
                logger.info(f"{key} in cache, returning.")
                value = eval(result)
            return value

        return wrapper


