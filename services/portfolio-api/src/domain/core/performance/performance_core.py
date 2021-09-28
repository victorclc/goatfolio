from typing import Optional, List, Dict

from domain.core.performance.calculators import (
    InvestmentPerformanceCalculator,
    GroupSummaryCalculator,
)
from domain.core.performance.historical_consolidators import (
    InvestmentHistoryConsolidator,
)
from domain.enums.investment_type import InvestmentType
from domain.models.group_position_summary import GroupPositionSummary
from domain.models.investment_consolidated import StockConsolidated
from domain.models.performance import (
    PerformanceSummary,
    PortfolioHistory,
    TickerConsolidatedHistory,
)
from domain.models.portfolio import Portfolio
from domain.ports.outbound.portfolio_repository import PortfolioRepository


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

    def portfolio_history_chart(self, subject: str):
        _, consolidations = self.repo.find_all(subject)

        positions = self.history_consolidators[
            InvestmentType.STOCK
        ].consolidate_historical_data_monthly(consolidations)

        return PortfolioHistory(positions, [])

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
