from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from domain.core.investment.investment_core import InvestmentCore
from domain.core.performance.performance_core import PerformanceCore
from domain.core.portfolio.portfolio_core import PortfolioCore

investment_core = InvestmentCore(repo=DynamoInvestmentRepository())
portfolio_core = PortfolioCore(repo=DynamoPortfolioRepository())
performance_core = PerformanceCore(DynamoPortfolioRepository())
