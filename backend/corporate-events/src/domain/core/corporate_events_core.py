import datetime
import logging
from decimal import Decimal
from itertools import groupby
from typing import Callable, List, Dict

from domain.enums.event_type import EventType
from domain.enums.operation_type import OperationType
from domain.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from domain.models.stock_investment import StockInvestment
from domain.models.ticker_transformation import TickerTransformation
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
            [
                str,
                str,
                EarningsInAssetCorporateEvent,
                List[StockInvestment],
                TickerInfoClient,
            ],
            List[StockInvestment],
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
                new_investments = strategy(
                    subject, ticker, event, list(investments), self.ticker
                )
                if new_investments:
                    self.investments.batch_save(new_investments)

    def check_for_applicable_corporate_events(
        self, subject, investments, strategies: Dict[EventType, Callable]
    ):
        investments = filter(
            lambda i: i.operation in [OperationType.BUY, OperationType.SELL]
            and not i.alias_ticker,
            investments,
        )
        investments_map = groupby(
            sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker
        )

        for ticker, investments in investments_map:
            investments = list(investments)
            oldest = min([i.date for i in investments])
            isin_code = self.ticker.get_isin_code_from_ticker(ticker)
            events = self.events.find_by_isin_from_date(isin_code, oldest)

            if not events:
                continue

            all_ticker_investments = self.investments.find_by_subject_and_ticker(
                subject, ticker
            )
            for event in events:
                logger.info(f"handling event {event} for {subject}")
                affected_investments = list(
                    filter(
                        lambda i, with_date=event.with_date: i.date <= with_date,
                        all_ticker_investments,
                    )
                )
                new_investments = strategies[event.type](
                    subject, ticker, event, list(affected_investments), self.ticker
                )
                if new_investments:
                    self.investments.batch_save(new_investments)

    def transformations_in_ticker(self, current_ticker: str, date_from: datetime.date):
        ticker = current_ticker
        isin = self.ticker.get_isin_code_from_ticker(ticker)
        events_list = self.events.find_by_isin_from_date(isin, date_from)

        tmp = self.events.find_by_type_and_emitted_asset(
            EventType.INCORPORATION, isin, date_from
        )
        if tmp:
            previous_isin = tmp[0].isin_code
            ticker = self.ticker.get_ticker_from_isin_code(previous_isin)
            events_list += self.events.find_by_isin_from_date(previous_isin, date_from)

        factor = Decimal(1)
        for event in events_list:
            factor *= event.factor

        return TickerTransformation(ticker, factor)

    def get_corporate_events(self, ticker: str, date: datetime.date) -> List[EarningsInAssetCorporateEvent]:
        isin_code = self.ticker.get_isin_code_from_ticker(ticker)
        events = self.events.find_by_isin_from_date(isin_code, date)

        return events
