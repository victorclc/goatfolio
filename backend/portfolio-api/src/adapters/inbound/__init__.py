from adapters.outbound.cedro_stock_intraday_client import CedroStockIntradayClient
from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from adapters.outbound.dynamo_stock_history_repository import (
    DynamoStockHistoryRepository,
)
from adapters.outbound.rest_corporate_events_client import RESTCorporateEventsClient
from domain.performance.calculators import (
    StockPerformanceCalculator,
    StockGroupPositionCalculator,
)
from domain.performance.historical_consolidators import StockHistoryConsolidator
from domain.performance.performance_core import PerformanceCore
from domain.corporate_events import CorporateEventsConsolidationCore
from domain.investments.investment_consolidation_strategies import StockConsolidationStrategy
from domain.investments.investment_consolidation_core import InvestmentConsolidationCore
from domain.stock_average.stock_core import StockCore
from domain.common.investments import InvestmentType

investment_repo = DynamoInvestmentRepository()
portfolio_repo = DynamoPortfolioRepository()
intraday_client = CedroStockIntradayClient()
stock_history = DynamoStockHistoryRepository()
transformation_client = RESTCorporateEventsClient()
events_consolidated = CorporateEventsConsolidationCore(investment_repo, transformation_client)


portfolio_core = InvestmentConsolidationCore(
    repo=portfolio_repo,
    strategies={InvestmentType.STOCK: StockConsolidationStrategy(portfolio_repo)},
)
performance_core = PerformanceCore(
    portfolio_repo,
    calculators={
        InvestmentType.STOCK: StockPerformanceCalculator(stock_history, intraday_client)
    },
    group_calculators={
        InvestmentType.STOCK: StockGroupPositionCalculator(intraday_client)
    },
    history_consolidators={
        InvestmentType.STOCK: StockHistoryConsolidator(stock_history, intraday_client)
    },
)
stock_core = StockCore(portfolio_repo, investment_repo, transformation_client)
