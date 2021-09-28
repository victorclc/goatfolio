from typing import Optional, List

from adapters.outbound.cedro_stock_intraday_client import CedroStockIntradayClient
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from adapters.outbound.dynamo_stock_history_repository import (
    DynamoStockHistoryRepository,
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
from domain.core.performance.calculators import (
    StockPerformanceCalculator,
    StockGroupPositionCalculator,
)
from domain.core.performance.historical_consolidators import StockHistoricalConsolidator

from domain.ports.outbound.portfolio_repository import PortfolioRepository

CALCULATORS = {
    InvestmentType.STOCK: StockPerformanceCalculator(
        DynamoStockHistoryRepository(), CedroStockIntradayClient()
    )
}

HISTORICAL_CONSOLIDATOR = {
    InvestmentType.STOCK: StockHistoricalConsolidator(
        DynamoStockHistoryRepository(), CedroStockIntradayClient()
    ),
}

GROUPED_CALCULATOR = {
    InvestmentType.STOCK: StockGroupPositionCalculator(CedroStockIntradayClient())
}


class PerformanceCore:
    def __init__(self, portfolio_repo: PortfolioRepository):
        self.repo = portfolio_repo

    def get_portfolio(self, subject: str) -> Portfolio:
        return self.repo.find(subject) or Portfolio(subject=subject, ticker=subject)

    def calculate_portfolio_summary(self, subject: str) -> PerformanceSummary:
        portfolio = self.get_portfolio(subject)

        performance = CALCULATORS.get(
            InvestmentType.STOCK
        ).calculate_performance_summary(portfolio.active_stocks())

        return performance

    def portfolio_history_chart(self, subject: str):
        _, consolidations = self.repo.find_all(subject)

        positions = HISTORICAL_CONSOLIDATOR[
            InvestmentType.STOCK
        ].consolidate_historical_data_monthly(consolidations)

        return PortfolioHistory(positions, [])

    def ticker_history_chart(
        self, subject: str, ticker: str
    ) -> Optional[TickerConsolidatedHistory]:
        consolidations = self.repo.find_alias_ticker(subject, ticker, StockConsolidated)
        if not consolidations:
            return

        positions = HISTORICAL_CONSOLIDATOR[
            InvestmentType.STOCK
        ].consolidate_historical_data_monthly(consolidations)

        return TickerConsolidatedHistory(positions)

    def calculate_portfolio_detailed_summary(self, subject: str) -> List[GroupPositionSummary]:
        portfolio = self.get_portfolio(subject)

        performance = GROUPED_CALCULATOR.get(
            InvestmentType.STOCK
        ).calculate_group_position_summary(portfolio.stocks)

        return performance


def main():
    subject = "41e4a793-3ef5-4413-82e2-80919bce7c1a"
    core = PerformanceCore(DynamoPortfolioRepository())
    results = core.calculate_portfolio_detailed_summary(subject)
    dict_response = {
        summary.group_name: {
            "opened_positions": summary.opened_positions,
            "gross_value": summary.gross_value,
        }
        for summary in results
    }
    print(dict_response)


if __name__ == "__main__":
    main()
