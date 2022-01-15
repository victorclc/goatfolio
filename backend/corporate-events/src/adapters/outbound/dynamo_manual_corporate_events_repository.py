import datetime

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key, Attr

from application.models.earnings_in_assets_event import ManualEarningsInAssetCorporateEvents

logger = Logger()


class DynamoManualCorporateEventsRepository:
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("ManualCorporateEvents")

    def find_by_ticker_and_date(self, subject: str, ticker: str, date: datetime.date):
        assert ticker
        result = self.__table.query(
            KeyConditionExpression=Key("subject").eq(subject) & Key("id").begins_with(f"TICKER#{ticker}"),
            FilterExpression=Attr("last_date_prior").lte(int(date.strftime("%Y%m%d"))),
        )
        return list(map(lambda i: ManualEarningsInAssetCorporateEvents(**i), result["Items"]))

    def find_by_ticker_from_date(self, subject: str, ticker: str, date: datetime.date):
        assert ticker
        result = self.__table.query(
            KeyConditionExpression=Key("subject").eq(subject) & Key("id").begins_with(f"TICKER#{ticker}"),
            FilterExpression=Attr("last_date_prior").gte(int(date.strftime("%Y%m%d"))),
        )
        return list(map(lambda i: ManualEarningsInAssetCorporateEvents(**i), result["Items"]))

    def save(self, event: ManualEarningsInAssetCorporateEvents):
        self.__table.put_item(Item=event.to_dict())
