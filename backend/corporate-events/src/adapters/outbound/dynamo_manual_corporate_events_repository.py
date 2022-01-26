import datetime
from typing import List

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key, Attr

from application.enums.event_type import EventType
from application.models.earnings_in_assets_event import ManualEarningsInAssetCorporateEvents

logger = Logger()


class DynamoManualCorporateEventsRepository:
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("ManualCorporateEvents")

    def find_by_ticker_and_date(self, subject: str, ticker: str, date: datetime.date):
        assert ticker
        result = self.__table.query(
            KeyConditionExpression=Key("subject").eq(subject) & Key("id").begins_with(f"TICKER#{ticker}"),
            FilterExpression=Attr("last_date_prior").lte(date.strftime("%Y%m%d")),
        )
        return list(map(lambda i: ManualEarningsInAssetCorporateEvents(**i), result["Items"]))

    def find_by_ticker_from_date(self, subject: str, ticker: str, date: datetime.date):
        assert ticker
        result = self.__table.query(
            KeyConditionExpression=Key("subject").eq(subject) & Key("id").begins_with(f"TICKER#{ticker.upper()}#"),
            FilterExpression=Attr("last_date_prior").gte(date.strftime("%Y%m%d")),
        )
        return list(map(lambda i: ManualEarningsInAssetCorporateEvents(**i), result["Items"]))

    def find_by_emitted_ticker_from_date_and_event_type(
            self, subject, event_type: EventType, emitted_ticker: str, from_date: datetime.date
    ) -> List[ManualEarningsInAssetCorporateEvents]:
        result = self.__table.query(
            IndexName="subjectEmittedTickerGlobalIndex",
            KeyConditionExpression=Key("subject").eq(subject) & Key("emitted_ticker").eq(emitted_ticker),
            FilterExpression=Attr("type").eq(event_type.value) & Attr("last_date_prior").gt(
                from_date.strftime("%Y%m%d")),
        )
        return list(map(lambda i: ManualEarningsInAssetCorporateEvents(**i), result["Items"]))

    def save(self, event: ManualEarningsInAssetCorporateEvents):
        self.__table.put_item(Item=event.to_dict())
