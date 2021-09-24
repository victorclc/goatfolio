from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_portfolio_repository import DynamoPortfolioRepository
from domain.investment_core import InvestmentCore
from domain.performance_core import PerformanceCore
from domain.portfolio_core import PortfolioCore

investment_core = InvestmentCore(repo=DynamoInvestmentRepository())
portfolio_core = PortfolioCore(repo=DynamoPortfolioRepository())
performance_core = PerformanceCore(DynamoPortfolioRepository())
