import datetime
from typing import List

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key, Attr

from application.enums.event_type import EventType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent


logger = Logger()


class DynamoCorporateEventsRepository:
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("CorporateEvents")

    def find_by_isin_from_date(self, isin_code: str, date: datetime.date):
        result = self.__table.query(
            IndexName="isinDateGlobalIndex",
            KeyConditionExpression=Key("isin_code").eq(isin_code)
            & Key("with_date").gte(date.strftime("%Y%m%d")),
        )
        return list(map(lambda i: EarningsInAssetCorporateEvent(**i), result["Items"]))

    def find_by_type_and_date(
        self, event_type: EventType, date: datetime.date
    ) -> List[EarningsInAssetCorporateEvent]:
        result = self.__table.query(
            IndexName="typeDateLocalIndex",
            KeyConditionExpression=Key("type").eq(event_type.value)
            & Key("with_date").eq(date.strftime("%Y%m%d")),
        )
        return list(map(lambda i: EarningsInAssetCorporateEvent(**i), result["Items"]))

    def find_by_type_and_emitted_asset(
        self, event_type: EventType, emitted_isin: str, from_date: datetime.date
    ) -> List[EarningsInAssetCorporateEvent]:
        result = self.__table.query(
            IndexName="typeDateLocalIndex",
            KeyConditionExpression=Key("type").eq(event_type.value)
            & Key("with_date").gt(from_date.strftime("%Y%m%d")),
            FilterExpression=Attr("emitted_asset").eq(emitted_isin),
        )
        return list(map(lambda i: EarningsInAssetCorporateEvent(**i), result["Items"]))

    def batch_save(self, records: List[EarningsInAssetCorporateEvent]):
        logger.debug(f"BatchSaving records: {records}")
        with self.__table.batch_writer() as batch:
            for record in records:
                batch.put_item(Item=record.to_dict())
