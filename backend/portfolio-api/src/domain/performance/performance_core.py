from typing import Optional, List, Dict

from domain.performance.calculators import (
    InvestmentPerformanceCalculator,
    GroupSummaryCalculator,
)
from domain.performance.historical_consolidators import (
    InvestmentHistoryConsolidator,
)
from domain.common.investments import InvestmentType
from domain.performance.group_position_summary import GroupPositionSummary
from domain.common.investment_consolidated import StockConsolidated, InvestmentConsolidated
from domain.performance.performance import (
    PerformanceSummary,
    TickerConsolidatedHistory,
)
from domain.common.portfolio import Portfolio
from ports.outbound.portfolio_repository import PortfolioRepository


class PerformanceCore:
    def __init__(
        self,
        repo: PortfolioRepository,
        calculators: Dict[InvestmentType, InvestmentPerformanceCalculator],
        group_calculators: Dict[InvestmentType, GroupSummaryCalculator],
        history_consolidators: Dict[InvestmentType, InvestmentHistoryConsolidator],
    ):
        self.repo = repo
        self.calculators = calculators
        self.group_calculators = group_calculators
        self.history_consolidators = history_consolidators

    def get_portfolio(self, subject: str) -> Portfolio:
        return self.repo.find(subject) or Portfolio(subject=subject, ticker=subject)

    def calculate_portfolio_summary(self, subject: str) -> PerformanceSummary:
        portfolio = self.get_portfolio(subject)

        performance = self.calculators.get(
            InvestmentType.STOCK
        ).calculate_performance_summary(portfolio.active_stocks())

        return performance

    def portfolio_history_chart(self, subject: str) -> List[InvestmentConsolidated]:
        _, consolidations = self.repo.find_all(subject)

        positions = self.history_consolidators[
            InvestmentType.STOCK
        ].consolidate_historical_data_monthly(consolidations)

        return positions

    def ticker_history_chart(
        self, subject: str, ticker: str
    ) -> Optional[TickerConsolidatedHistory]:
        consolidations = self.repo.find_alias_ticker(subject, ticker, StockConsolidated)
        if not consolidations:
            return

        positions = self.history_consolidators[
            InvestmentType.STOCK
        ].consolidate_historical_data_monthly(consolidations)

        return TickerConsolidatedHistory(positions)

    def calculate_portfolio_detailed_summary(
        self, subject: str
    ) -> List[GroupPositionSummary]:
        portfolio = self.get_portfolio(subject)

        performance = self.group_calculators.get(
            InvestmentType.STOCK
        ).calculate_group_position_summary(portfolio.stocks)

        return performance
