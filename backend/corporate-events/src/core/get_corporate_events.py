from datetime import datetime
from typing import List, Optional, Protocol

from aws_lambda_powertools import Logger

from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent, \
    ManualEarningsInAssetCorporateEvents
from application.ports.corporate_events_repository import CorporateEventsRepository
from application.ports.ticker_info_client import TickerInfoClient
from application.converters import earnings_converter

logger = Logger()


class ManualCorporateEventsRepository(Protocol):
    def find_by_ticker_from_date(self, subject: str, ticker: str, from_date: datetime.date) -> List[
        ManualEarningsInAssetCorporateEvents
    ]:
        ...


def get_corporate_events(
        ticker: str,
        date: datetime.date,
        ticker_info: TickerInfoClient,
        repository: CorporateEventsRepository,
        manual_events_repo: ManualCorporateEventsRepository,
        subject: Optional[str] = None
) -> List[EarningsInAssetCorporateEvent]:
    isin_code = ticker_info.get_isin_code_from_ticker(ticker)
    events = repository.find_by_isin_from_date(isin_code, date)

    for event in events:
        if event.emitted_asset:
            event.emitted_ticker = ticker_info.get_ticker_from_isin_code(
                event.emitted_asset
            )

    if subject:
        manual_events = manual_events_repo.find_by_ticker_from_date(subject, ticker, date)
        logger.info(f"Found {len(manual_events)} manual events for subject {subject}")
        events += list(map(lambda e: earnings_converter.manual_earning_to_earnings_in_assets_converter(e, ticker_info),
                           manual_events))

    return events
