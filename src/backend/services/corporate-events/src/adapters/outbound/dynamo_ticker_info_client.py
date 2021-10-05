import boto3
from boto3.dynamodb.conditions import Key


class DynamoTickerInfoClient:
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
