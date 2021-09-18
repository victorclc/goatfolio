import logging
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key

from domain.models.portfolio import Portfolio, StockConsolidated

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynamoPortfolioRepository:
    def __init__(self):
        self._portfolio_table = boto3.resource("dynamodb").Table("Portfolio")

    def find(self, subject: str) -> Portfolio:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("ticker").eq(subject)
        )
        if result["Items"]:
            return Portfolio(**result["Items"][0])
        logger.info(f"No Portfolio yet for subject: {subject}")
        return Portfolio(subject=subject, ticker=subject)

    def find_all(self, subject) -> (Portfolio, [StockConsolidated]):
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
        )
        portfolio = None
        stock_consolidated = []
        if not result["Items"]:
            logger.info(f"No Portfolio yet for subject: {subject}")
            return
        for item in result["Items"]:
            if item["ticker"] == subject:
                portfolio = Portfolio(**item)
            else:
                stock_consolidated.append(StockConsolidated(**item))
        return portfolio, stock_consolidated

    def find_ticker(
        self, subject: str, ticker: str
    ) -> Optional[List[StockConsolidated]]:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject) & Key("ticker").eq(ticker)
        )
        if result["Items"]:
            return [StockConsolidated(**i) for i in result["Items"]]
        logger.info(f"No {ticker} yet for subject: {subject}")

    def find_alias_ticker(
        self, subject: str, ticker: str
    ) -> Optional[List[StockConsolidated]]:
        result = self._portfolio_table.query(
            IndexName="subjectAliasTickerGlobalIndex",
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("alias_ticker").eq(ticker),
        )
        if result["Items"]:
            return [StockConsolidated(**i) for i in result["Items"]]
        logger.info(f"No alias {ticker} yet for subject: {subject}")
        return []

    def save_portfolio(self, portfolio: Portfolio) -> None:
        logger.info(f"Saving: {portfolio.to_dict()}")
        self._portfolio_table.put_item(Item=portfolio.to_dict())

    def save_stock_consolidated(self, stock_consolidated: StockConsolidated) -> None:
        logger.info(f"Saving: {stock_consolidated.to_dict()}")
        self._portfolio_table.put_item(Item=stock_consolidated.to_dict())
