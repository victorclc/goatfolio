from adapters.outbound.dynamo_corporate_events_repository import (
    DynamoCorporateEventsRepository,
)
from adapters.outbound.dynamo_investment_repository import DynamoInvestmentRepository
from adapters.outbound.dynamo_ticker_info_client import DynamoTickerInfoClient
from adapters.outbound.s3_coporate_events_file_storage import (
    S3CorporateEventsFileStorage,
)
from domain.core.corporate_events_core import CorporateEventsCore
from domain.core.corporate_events_crawler import B3CorporateEventsCrawler, B3CorporateEventsFileProcessor

events_repo = DynamoCorporateEventsRepository()
investment_repo = DynamoInvestmentRepository()
ticker_client = DynamoTickerInfoClient()
file_storage = S3CorporateEventsFileStorage()

corporate_events_core = CorporateEventsCore(events_repo, ticker_client, investment_repo)
corporate_events_crawler = B3CorporateEventsCrawler(file_storage)
corporate_events_file_processor = B3CorporateEventsFileProcessor(file_storage, events_repo)