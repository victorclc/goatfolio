from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.sns_investment_publisher import SNSInvestmentPublisher
from domain.core import InvestmentCore

repo = DynamoInvestmentRepository()
publisher = SNSInvestmentPublisher()

investment_core = InvestmentCore(repo=DynamoInvestmentRepository(), publisher=publisher)
