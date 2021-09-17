import logging

import boto3
from boto3.dynamodb.conditions import Key

from goatcommons.portfolio.models import Portfolio, StockConsolidated

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PortfolioRepository:
    def __init__(self):
        self._portfolio_table = boto3.resource("dynamodb").Table("Portfolio")

    def find(self, subject) -> Portfolio:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("ticker").eq(subject)
        )
        if result["Items"]:
            return Portfolio(**result["Items"][0])
        logger.info(f"No Portfolio yet for subject: {subject}")
        return Portfolio(subject=subject, ticker=subject)

    def find_ticker(self, subject, ticker) -> [StockConsolidated]:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject) & Key("ticker").eq(ticker)
        )
        if result["Items"]:
            return [StockConsolidated(**i) for i in result["Items"]]
        logger.info(f"No {ticker} yet for subject: {subject}")

    def find_alias_ticker(self, subject, ticker) -> [StockConsolidated]:
        result = self._portfolio_table.query(
            IndexName="subjectAliasTickerGlobalIndex",
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("alias_ticker").eq(ticker),
        )
        if result["Items"]:
            return [StockConsolidated(**i) for i in result["Items"]]
        logger.info(f"No alias {ticker} yet for subject: {subject}")
        return []

    def save(self, obj):
        logger.info(f"Saving: {obj.to_dict()}")
        self._portfolio_table.put_item(Item=obj.to_dict())
