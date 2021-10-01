import datetime
from typing import List

import boto3
from boto3.dynamodb.conditions import Key, Attr

from domain.models.stock_investment import StockInvestment


class DynamoInvestmentRepository:
    def __init__(self):
        self.__investments_table = boto3.resource("dynamodb").Table("Investments")

    def find_by_subject_and_ticker(self, subject, ticker) -> List[StockInvestment]:
        result = self.__investments_table.query(
            KeyConditionExpression=Key("subject").eq(subject),
            FilterExpression=Attr("ticker").eq(ticker),
        )
        return list(map(lambda i: StockInvestment(**i), result["Items"]))

    def find_by_ticker_until_date(
        self, ticker, with_date: datetime.date
    ) -> List[StockInvestment]:
        result = self.__investments_table.query(
            IndexName="tickerSubjectGlobalIndex",
            KeyConditionExpression=Key("ticker").eq(ticker),
            FilterExpression=Attr("date").lte(int(with_date.strftime("%Y%m%d"))),
        )
        return list(map(lambda i: StockInvestment(**i), result["Items"]))

    def batch_save(self, investments: List[StockInvestment]):
        with self.__investments_table.batch_writer() as batch:
            for investment in investments:
                print(investment.to_dict())
                batch.put_item(Item=investment.to_dict())
