from abc import abstractmethod, ABC
from itertools import groupby
from typing import List, Callable, Any, Optional

from domain.models.investment import Investment, StockInvestment
from domain.models.investment_consolidated import (
    InvestmentConsolidated,
    StockConsolidated,
)


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
