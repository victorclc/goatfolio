from typing import Optional

from aws_lambda_powertools import Logger

from application.models.cash_dividends_summary import CashDividendsSummary
from domain.common.investments import StockDividend
from ports.outbound.portfolio_repository import PortfolioRepository

logger = Logger()


class NewCashDividendListener:
    def __init__(self, portfolio_repository: PortfolioRepository):
        self.portfolio_repository = portfolio_repository

    def receive(
            self, subject: str, new: Optional[StockDividend], old: Optional[StockDividend]
    ):
        summary = self.portfolio_repository.find_dividends_summary(subject) or CashDividendsSummary(subject)
        logger.info(f"Before consolidation summary: {summary}")
        if new:
            summary.add_dividend(new)
        if old:
            old.amount *= -1
            summary.add_dividend(old)
        logger.info(f"Saving summary: {summary}")
        self.portfolio_repository.save(summary)
