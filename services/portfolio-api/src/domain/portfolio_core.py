import logging
from itertools import groupby
from typing import List, Dict, Set

from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from domain.consolidation_strategies import (
    InvestmentsConsolidationStrategy,
    StockConsolidationStrategy,
)
from domain.enums.investment_type import InvestmentType
from domain.models.investment import Investment
from domain.models.portfolio import (
    Portfolio,
    InvestmentConsolidated,
)
from domain.ports.outbound.portfolio_repository import PortfolioRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


CONSOLIDATE_STRATS: Dict[InvestmentType, InvestmentsConsolidationStrategy] = {
    InvestmentType.STOCK: StockConsolidationStrategy(DynamoPortfolioRepository())
}


class PortfolioCore:
    def __init__(
        self,
        repo: PortfolioRepository,
    ):
        self.repo = repo

    def consolidate_investments(
        self, subject: str, new: List[Investment], old: List[Investment]
    ):
        portfolio = self.get_portfolio(subject)
        all_items: List[InvestmentConsolidated] = []
        for _type in self.types_of_investments_in(new + old):
            filtered_new = list(filter(lambda i, t=_type: i.type == t, new))
            filtered_old = list(filter(lambda i, t=_type: i.type == t, old))

            all_items += CONSOLIDATE_STRATS[_type].consolidate(
                subject,
                filtered_new,
                filtered_old
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


def main():
    subject = "41e4a793-3ef5-4413-82e2-80919bce7c1a"
    investments = DynamoInvestmentRepository().find_by_subject(subject)
    core = PortfolioCore(repo=DynamoPortfolioRepository())
    core.consolidate_investments(subject, investments, [])


if __name__ == "__main__":
    main()
