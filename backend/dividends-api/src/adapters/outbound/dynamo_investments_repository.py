from datetime import datetime
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key, Attr

from application.models.invesments import StockInvestment


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_ticker_until_date(
            self, ticker: str, until_date: datetime.date, subject: Optional[str] = None
    ) -> List[StockInvestment]:
        key_condition = Key("ticker").eq(ticker)
        if subject:
            key_condition &= Key("subject").eq(subject)

        result = self.__investments_table.query(
            IndexName="tickerSubjectGlobalIndex",
            KeyConditionExpression=key_condition,
            FilterExpression=Attr("date").lte(int(until_date.strftime("%Y%m%d"))),
        )
        return list(map(lambda i: StockInvestment(**i), result["Items"]))
