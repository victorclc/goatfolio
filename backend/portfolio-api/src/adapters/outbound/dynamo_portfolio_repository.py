import logging
from typing import List, Optional, ClassVar, Type

import boto3
from boto3.dynamodb.conditions import Key, Attr

from domain.common.investment_consolidated import StockConsolidated
from domain.common.portfolio import (
    Portfolio,
    PortfolioItem,
    InvestmentConsolidated,
)
from domain.stock_average.assets_quantities import AssetQuantities

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
            & Key("sk").eq("PORTFOLIO#")
        )
        if result["Items"]:
            return Portfolio(
                **{k: v for k, v in result["Items"][0].items() if k != "sk"}
            )
        logger.info(f"No Portfolio yet for subject: {subject}")

    def find_all(self, subject) -> (Portfolio, [InvestmentConsolidated]):
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
        )
        portfolio = None
        stock_consolidated = []
        if not result["Items"]:
            logger.info(f"No Portfolio yet for subject: {subject}")
            return
        for item in result["Items"]:
            sk = item.pop("sk")
            if sk == "PORTFOLIO#":
                portfolio = Portfolio(**item)
            if sk.startswith("TICKER#"):
                stock_consolidated.append(StockConsolidated(**item))
        return portfolio, stock_consolidated

    def find_ticker(
        self,
        subject: str,
        ticker: str,
        consolidated_type: ClassVar[Type[InvestmentConsolidated]],
    ) -> Optional[List[Type[InvestmentConsolidated]]]:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("sk").begins_with(f"TICKER#{ticker.upper()}")
        )
        if result["Items"]:
            return [
                consolidated_type(**{k: v for k, v in i.items() if k != "sk"})
                for i in result["Items"]
            ]
        logger.info(f"No {ticker} yet for subject: {subject}")
        return []

    def find_asset_quantities(self, subject: str) -> Optional[AssetQuantities]:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("sk").begins_with(f"STOCKQUANTITIES#")
        )
        if result["Items"]:
            return AssetQuantities(
                **{k: v for k, v in result["Items"][0].items() if k != "sk"}
            )
        logger.info(f"No Asset quantities for subject: {subject}")

    def find_alias_ticker(
        self,
        subject: str,
        ticker: str,
        consolidated_type: ClassVar[Type[InvestmentConsolidated]],
    ) -> Optional[List[InvestmentConsolidated]]:
        result = self._portfolio_table.query(
            KeyConditionExpression=Key("subject").eq(subject)
            & Key("sk").begins_with(f"TICKER#"),
            FilterExpression=Attr("alias_ticker").eq(ticker),
        )
        if result["Items"]:
            return [
                consolidated_type(**{k: v for k, v in i.items() if k != "sk"})
                for i in result["Items"]
            ]
        logger.info(f"No alias {ticker} yet for subject: {subject}")
        return []

    def save(self, item: PortfolioItem):
        self._portfolio_table.put_item(Item=item.to_json())

    def save_all(self, items: [PortfolioItem]):
        with self._portfolio_table.batch_writer() as batch:
            for item in items:
                print(item.to_json())
                batch.put_item(Item=item.to_json())
