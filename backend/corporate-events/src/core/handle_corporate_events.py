from datetime import datetime
from itertools import groupby
from typing import Callable, List

from aws_lambda_powertools import Logger

from application.enums.event_type import EventType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from application.models.stock_investment import StockInvestment
from application.ports.corporate_events_repository import CorporateEventsRepository
from application.ports.investment_repository import InvestmentRepository
from application.ports.ticker_info_client import TickerInfoClient

logger = Logger()


def handle_corporate_events(
        event_type: EventType,
        date: datetime.date,
        strategy: Callable[
            [
                str,
                str,
                EarningsInAssetCorporateEvent,
                List[StockInvestment],
                TickerInfoClient,
            ],
            List[StockInvestment],
        ],
        ticker_info: TickerInfoClient,
        repository: CorporateEventsRepository,
        investments_repo: InvestmentRepository

):
    events = repository.find_by_type_and_date(event_type, date)
    logger.info(f"Events to process: {events}")
    for event in events:
        logger.info(f"Processing event: {event}")
        ticker = ticker_info.get_ticker_from_isin_code(event.isin_code)
        investments = sorted(
            investments_repo.find_by_ticker_until_date(ticker, event.with_date),
            key=lambda i: i.subject,
        )
        for subject, investments in groupby(investments, key=lambda i: i.subject):
            logger.info(f"handling {subject}")
            new_investments = strategy(
                subject, ticker, event, list(investments), ticker_info
            )
            if new_investments:
                investments_repo.batch_save(new_investments)
