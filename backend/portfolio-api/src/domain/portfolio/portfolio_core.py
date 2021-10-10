import logging
from itertools import groupby
from typing import List, Dict, Set

from domain.portfolio.consolidation_strategies import (
    InvestmentsConsolidationStrategy,
)
from domain.enums.investment_type import InvestmentType
from domain.models.investment import Investment
from domain.common.portfolio import (
    Portfolio,
    InvestmentConsolidated,
)
from ports.outbound.portfolio_repository import PortfolioRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PortfolioCore:
    def __init__(
        self,
        repo: PortfolioRepository,
        strategies: Dict[InvestmentType, InvestmentsConsolidationStrategy],
    ):
        self.repo = repo
        self.strategies = strategies

    def consolidate_investments(
        self, subject: str, new: List[Investment], old: List[Investment]
    ):
        portfolio = self.get_portfolio(subject)
        all_items: List[InvestmentConsolidated] = []
        for _type in self.types_of_investments_in(new + old):
            filtered_new = list(filter(lambda i, t=_type: i.type == t, new))
            filtered_old = list(filter(lambda i, t=_type: i.type == t, old))

            all_items += self.strategies[_type].consolidate(
                subject, filtered_new, filtered_old
            )
        portfolio.update_summary(all_items)
        self.repo.save(portfolio)

    def get_portfolio(self, subject) -> Portfolio:
        portfolio = self.repo.find(subject) or Portfolio(
            subject=subject, ticker=subject
        )
        return portfolio

    @staticmethod
    def group_by_investment_type(investments: List[Investment]):
        return groupby(sorted(investments, key=lambda i: i.type), key=lambda i: i.type)

    @staticmethod
    def types_of_investments_in(investments: List[Investment]) -> Set[InvestmentType]:
        return set([inv.type for inv in investments])
