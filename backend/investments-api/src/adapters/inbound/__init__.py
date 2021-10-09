from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from domain.core import InvestmentCore

investment_repo = DynamoInvestmentRepository()
investment_core = InvestmentCore(repo=DynamoInvestmentRepository())