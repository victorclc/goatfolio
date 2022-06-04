from typing import Protocol, Optional

from aws_lambda_powertools import Logger

from application.investment import Investment, StockInvestment, StockDividend

logger = Logger()


class InvestmentPublisher(Protocol):
    def publish_stock_investment(
            self,
            subject: str,
            updated_timestamp: int,
            new_investment: Optional[StockInvestment],
            old_investment: Optional[StockInvestment],
    ):
        ...

    def publish_stock_dividend(
            self,
            subject: str,
            updated_timestamp: int,
            new_investment: Optional[StockDividend],
            old_investment: Optional[StockDividend],
    ):
        ...


def is_stock_investment(new, old):
    return isinstance(new, StockInvestment) or isinstance(old, StockInvestment)


def is_stock_dividend(new, old):
    return isinstance(new, StockDividend) or isinstance(old, StockDividend)


def publish_investment_update(
        publisher: InvestmentPublisher,
        subject: str,
        updated_timestamp: int,
        new_investment: Optional[Investment],
        old_investment: Optional[Investment]
):
    if is_stock_investment(new_investment, old_investment):
        logger.info(
            f"Publishing StockInvestment: "
            f"subject={subject}, new_investment={new_investment}, old_investment{old_investment}"
        )
        publisher.publish_stock_investment(
            subject, updated_timestamp, new_investment=new_investment, old_investment=old_investment
        )
    elif is_stock_dividend(new_investment, old_investment):
        logger.info(
            f"Publishing StockDividend: "
            f"subject={subject}, new_investment={new_investment}, old_investment{old_investment}"
        )
        publisher.publish_stock_dividend(
            subject, updated_timestamp, new_investment=new_investment, old_investment=old_investment
        )
    else:
        logger.info(
            f"Unknown Investment type: "
            f"subject={subject}, new_investment={new_investment}, old_investment{old_investment}"
        )
