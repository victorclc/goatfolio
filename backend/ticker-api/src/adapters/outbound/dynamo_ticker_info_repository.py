
from typing import List

import boto3
from boto3.dynamodb.conditions import Key

from application.models.ticker_info import TickerInfo

from application.ports.ticker_info_repository import TickerInfoRepository


class DynamoTickerInfoRepository(TickerInfoRepository):
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("TickerInfo")

    def get_isin_code_from_ticker(self, ticker: str) -> str:
        result = self.__table.query(KeyConditionExpression=Key("ticker").eq(ticker))
        if result["Items"]:
            return result["Items"][0]["isin"]

    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        result = self.__table.query(
            IndexName="isinGlobalIndex",
            KeyConditionExpression=Key("isin").eq(isin_code),
        )
        if result["Items"]:
            return result["Items"][0]["ticker"]


    def find_by_code(self, code: str) -> List[TickerInfo]:
        result = self.__table.query(
            IndexName="codeIsinGlobalIndex",
            KeyConditionExpression=Key("code").eq(code.upper()),
        )
        if result["Items"]:
            return [TickerInfo(**i) for i in result["Items"]]
        return []

