from abc import abstractmethod, ABC
from typing import List, Optional

from domain.common.investment_consolidated import (
    InvestmentConsolidated,
    StockConsolidated,
)
from domain.common.investments import Investment, StockInvestment
from ports.outbound.portfolio_repository import PortfolioRepository


class InvestmentsConsolidationStrategy(ABC):
    @abstractmethod
    def consolidate(
        self,
        subject: str,
        new: Optional[Investment],
        old: Optional[Investment],
    ) -> List[InvestmentConsolidated]:
        """Consolidate new and old investments using as base current portfolio object and returns a new portfolio"""


class StockConsolidationStrategy(InvestmentsConsolidationStrategy):
    def __init__(self, portfolio_repo: PortfolioRepository):
        self.repo = portfolio_repo

    def consolidate(
        self,
        subject: str,
        new: Optional[StockInvestment],
        old: Optional[StockInvestment],
    ) -> InvestmentConsolidated:
        consolidated_list = []

        if new:
            consolidated_list = self.consolidate_investment(new, consolidated_list)
        if old:
            self.invert_investment_amount(old)
            consolidated_list = self.consolidate_investment(old, consolidated_list)

        self.repo.save_all(consolidated_list)

        return sum(consolidated_list[1:], consolidated_list[0])

    @staticmethod
    def invert_investment_amount(investment: StockInvestment):
        investment.amount *= -1

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

    def append_alias_consolidated_list_if_needed(
        self, investment: StockInvestment, consolidated_list: List[StockConsolidated]
    ):
        alias_consolidated = self.find_ticker_consolidated(
            investment.alias_ticker, consolidated_list
        )
        if not alias_consolidated:
            alias_list = self.repo.find_alias_ticker(
                investment.subject, investment.alias_ticker, StockConsolidated
            )
            if alias_list:
                consolidated_list += alias_list

    def consolidate_investment(
        self, investment: StockInvestment, consolidated_list: List[StockConsolidated]
    ) -> List[StockConsolidated]:
        consolidated_copy = consolidated_list.copy()

        if investment.alias_ticker:
            self.append_alias_consolidated_list_if_needed(investment, consolidated_copy)

        consolidated = self.find_ticker_consolidated(
            investment.ticker, consolidated_copy
        )
        if not consolidated:
            response = self.repo.find_ticker(
                investment.subject, investment.ticker, StockConsolidated
            )
            if response:
                consolidated = response[0]
            else:
                consolidated = StockConsolidated(
                    subject=investment.subject, ticker=investment.ticker
                )
            consolidated_copy.append(consolidated)

        consolidated.add_investment(investment)

        return consolidated_copy
