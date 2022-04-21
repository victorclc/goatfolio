from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.rest_ticker_info_client import RestTickerInfoClient
from adapters.outbound.sns_investment_publisher import SNSInvestmentPublisher
from core.crud import InvestmentCore

repo = DynamoInvestmentRepository()
publisher = SNSInvestmentPublisher()
ticker_info = RestTickerInfoClient()

investment_core = InvestmentCore(repo=DynamoInvestmentRepository(), publisher=publisher, ticker=ticker_info)
