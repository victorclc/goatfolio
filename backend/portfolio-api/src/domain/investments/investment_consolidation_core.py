import logging
from itertools import groupby
from typing import List, Dict, Set, Optional

from application.ports.ticker_info_client import TickerInfoClient
from domain.common.investments import InvestmentType, Investment
from domain.common.portfolio import (
    Portfolio,
)
from domain.investments.investment_consolidation_strategies import (
    InvestmentsConsolidationStrategy,
)
from ports.outbound.portfolio_repository import PortfolioRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class InvestmentConsolidationCore:
    def __init__(
        self,
        repo: PortfolioRepository,
        ticker_client: TickerInfoClient,
        strategies: Dict[InvestmentType, InvestmentsConsolidationStrategy],
    ):
        self.repo = repo
        self.strategies = strategies
        self.ticker_client = ticker_client

    def consolidate_investments(
        self, subject: str, new: Optional[Investment], old: Optional[Investment]
    ):
        portfolio = self.get_portfolio(subject)
        if new:
            if not self.ticker_client.is_ticker_valid(new.ticker):
                logger.warning(f"NEW TICKER IS NOT VALID: {new.ticker}")
                new = None
        if old:
            if not self.ticker_client.is_ticker_valid(old.ticker):
                logger.warning(f"OLD TICKER IS NOT VALID: {old.ticker}")
                old = None

        if not new and not old:
            return

        _type = self.get_type_if_investment(new, old)
        inv_consolidated = self.strategies[_type].consolidate(subject, new, old)
        portfolio.update_summary(inv_consolidated)
        self.repo.save(portfolio)

    @staticmethod
    def get_type_if_investment(new: Optional[Investment], old: Optional[Investment]):
        if new:
            return new.type
        if old:
            return old.type

    def get_portfolio(self, subject) -> Portfolio:
        portfolio = self.repo.find(subject) or Portfolio(
            subject=subject
        )
        return portfolio

    @staticmethod
    def group_by_investment_type(investments: List[Investment]):
        return groupby(sorted(investments, key=lambda i: i.type), key=lambda i: i.type)

    @staticmethod
    def types_of_investments_in(investments: List[Investment]) -> Set[InvestmentType]:
        return set([inv.type for inv in investments])
