from adapters.outbound.dynamo_cash_dividends_repository import DynamoCashDividendsRepository
from adapters.outbound.dynamo_corporate_events_repository import (
    DynamoCorporateEventsRepository,
)
from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.rest_b3_fetch_events_client import RESTB3EventsClient
from adapters.outbound.rest_ticker_info_client import RESTTickerInfoClient
from adapters.outbound.s3_coporate_events_file_storage import (
    S3CorporateEventsFileStorage,
)

events_repo = DynamoCorporateEventsRepository()
cash_dividends_repo = DynamoCashDividendsRepository()
investment_repo = DynamoInvestmentRepository()
ticker_client = RESTTickerInfoClient()
file_storage = S3CorporateEventsFileStorage()
events_client = RESTB3EventsClient()
