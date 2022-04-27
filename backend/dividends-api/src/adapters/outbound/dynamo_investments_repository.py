from datetime import datetime
from typing import List

import boto3
from boto3.dynamodb.conditions import Key, Attr

from application.models.invesments import StockInvestment


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_ticker_until_date(
            self, ticker, until_date: datetime.date
    ) -> List[StockInvestment]:
        result = self.__investments_table.query(
            IndexName="tickerSubjectGlobalIndex",
            KeyConditionExpression=Key("ticker").eq(ticker),
            FilterExpression=Attr("date").lte(int(until_date.strftime("%Y%m%d"))),
        )
        return list(map(lambda i: StockInvestment(**i), result["Items"]))
