import datetime
from typing import List
import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Key

from application.entities.cash_dividends import CashDividendsEntity

logger = Logger()


class DynamoCashDividendsRepository:
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("CashDividends")

    def save(self, event: CashDividendsEntity):
        self.__table.put_item(Item=event.to_dict())

    def batch_save(self, records: List[CashDividendsEntity]):
        logger.debug(f"BatchSaving records: {records}")
        with self.__table.batch_writer() as batch:
            for record in records:
                batch.put_item(Item=record.to_dict())

    def find_by_payment_date(self, payment_date: datetime.date) -> List[CashDividendsEntity]:
        result = self.__table.query(
            IndexName="paymentDateAssetIssuedGlobalIndex",
            KeyConditionExpression=Key("payment_date").eq(payment_date.strftime("%Y%m%d"))
        )
        return list(map(lambda i: CashDividendsEntity(**i), result["Items"]))

    def find_by_from_last_date_prior(self, isin: str, from_date: datetime.date) -> List[CashDividendsEntity]:
        result = self.__table.query(
            IndexName="assetIssueLastDatePriorLocalIndex",
            KeyConditionExpression=Key("asset_issued").eq(isin) & Key("last_date_prior").gte(
                from_date.strftime("%Y%m%d"))
        )
        return list(map(lambda i: CashDividendsEntity(**i), result["Items"]))
