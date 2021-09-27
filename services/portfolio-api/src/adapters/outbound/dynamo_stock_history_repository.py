import logging
from datetime import datetime
from typing import List, Optional, Dict

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer

from domain.models.performance import CandleData

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
    ) -> Dict[datetime.date, CandleData]:
        result = self.__table.query(
            KeyConditionExpression=Key("ticker").eq(ticker)
            & Key("candle_date").gte(_date.strftime(self.DATE_FORMAT))
        )

        candles = {}
        if result["Items"]:
            for item in result["Items"]:
                candle = CandleData(**item)
                candles[candle.candle_date] = candle

        return candles

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
