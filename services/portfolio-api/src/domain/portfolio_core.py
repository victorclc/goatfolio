import logging
from abc import ABC, abstractmethod
from itertools import groupby
from typing import List, Dict, Set, Callable, Optional, Any

from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from domain.enums.investment_type import InvestmentType
from domain.models.investment import StockInvestment, Investment
from domain.models.investment_consolidated import StockConsolidated
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


class InvestmentsConsolidationStrategy(ABC):
    @abstractmethod
    def consolidate(
        self,
        subject: str,
        new: List[Investment],
        old: List[Investment],
        find_consolidated_by_ticker_fn: Callable[
            [str, str, Any],
            List[InvestmentConsolidated],
        ],
        find_consolidated_by_alias_fn: Callable[
            [str, str, Any],
            List[InvestmentConsolidated],
        ],
    ) -> List[InvestmentConsolidated]:
        """Consolidate new and old investments using as base current portfolio object and returns a new portfolio"""


class StockConsolidationStrategy(InvestmentsConsolidationStrategy):
    def consolidate(
        self,
        subject: str,
        new: List[StockInvestment],
        old: List[StockInvestment],
        find_consolidated_fn: Callable[[str, str, Any], List[StockConsolidated]],
        find_consolidated_by_alias_fn: Callable[
            [str, str, Any], List[StockConsolidated]
        ],
    ) -> List[InvestmentConsolidated]:
        self.invert_investments_amount_list(old)
        consolidated_response = []

        for current_ticker, investments in self.group_by_current_ticker_name(new + old):
            consolidated_list = find_consolidated_by_alias_fn(
                subject, current_ticker, StockConsolidated
            )

            for ticker, t_investments in self.group_by_ticker(list(investments)):
                consolidated = self.find_ticker_consolidated(ticker, consolidated_list)
                if not consolidated:
                    response = find_consolidated_fn(subject, ticker, StockConsolidated)
                    if response:
                        consolidated = response[0]
                    else:
                        consolidated = StockConsolidated(subject=subject, ticker=ticker)
                    consolidated_list.append(consolidated)
                for inv in t_investments:
                    consolidated.add_investment(inv)
            consolidated_response.append(
                sum(consolidated_list[1:], consolidated_list[0])
            )

        return consolidated_response

    @staticmethod
    def invert_investments_amount_list(investments: List[StockInvestment]):
        for i in investments:
            i.amount *= -1

    @staticmethod
    def group_by_current_ticker_name(investments: List[StockInvestment]):
        by_ticker = groupby(
            sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker
        )
        for ticker, t_investments in by_ticker:
            t_investments = list(t_investments)
            alias_ticker = next(
                (i.alias_ticker for i in t_investments if i.alias_ticker), None
            )
            if alias_ticker:
                for i in t_investments:
                    i.alias_ticker = alias_ticker
        return groupby(
            sorted(investments, key=lambda i: i.current_ticker_name),
            key=lambda i: i.current_ticker_name,
        )

    @staticmethod
    def group_by_ticker(investments):
        return groupby(
            sorted(list(investments), key=lambda i: i.ticker),
            key=lambda i: i.ticker,
        )

    @staticmethod
    def find_ticker_consolidated(
        ticker: str, consolidated_list: List[StockConsolidated]
    ) -> Optional[StockConsolidated]:
        return next(
            (
                stock
                for stock in consolidated_list
                if stock.ticker == ticker or stock.alias_ticker == ticker
            ),
            None,
        )


CONSOLIDATE_STRATS: Dict[InvestmentType, InvestmentsConsolidationStrategy] = {
    InvestmentType.STOCK: StockConsolidationStrategy()
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
                filtered_old,
                self.repo.find_ticker,
                self.repo.find_alias_ticker,
            )
        portfolio.update_summary(all_items)
        self.repo.save_all([portfolio, *all_items])

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
