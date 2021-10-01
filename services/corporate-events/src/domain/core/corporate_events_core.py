import datetime
import logging
from itertools import groupby
from typing import Callable, List

from domain.enums.event_type import EventType
from domain.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from domain.models.stock_investment import StockInvestment
from domain.ports.outbound.corporate_events_repository import CorporateEventsRepository
from domain.ports.outbound.investment_repository import InvestmentRepository
from domain.ports.outbound.ticker_info_client import TickerInfoClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CorporateEventsCore:
    def __init__(
        self,
        events: CorporateEventsRepository,
        ticker: TickerInfoClient,
        investments: InvestmentRepository,
    ):
        self.events = events
        self.ticker = ticker
        self.investments = investments

    def handle_corporate_events(
        self,
        event_type: EventType,
        date: datetime.date,
        strategy: Callable[
            [str, str, EarningsInAssetCorporateEvent, List[StockInvestment]], None
        ],
    ):
        events = self.events.find_by_type_and_date(event_type, date)
        logger.info(f"Events to process: {events}")
        for event in events:
            logger.info(f"Processing event: {event}")
            ticker = self.ticker.get_ticker_from_isin_code(event.isin_code)
            investments = sorted(
                self.investments.find_by_ticker_until_date(ticker, event.with_date),
                key=lambda i: i.subject,
            )
            for subject, investments in groupby(investments, key=lambda i: i.subject):
                logger.info(f"handling {subject}")
                strategy(subject, ticker, event, list(investments))

