from datetime import datetime
from typing import List

from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from application.ports.corporate_events_repository import CorporateEventsRepository
from application.ports.ticker_info_client import TickerInfoClient


def get_corporate_events(
        ticker: str, date: datetime.date,
        ticker_info: TickerInfoClient, repository: CorporateEventsRepository
) -> List[EarningsInAssetCorporateEvent]:
    isin_code = ticker_info.get_isin_code_from_ticker(ticker)
    events = repository.find_by_isin_from_date(isin_code, date)

    for event in events:
        if event.emitted_asset:
            event.emitted_ticker = ticker_info.get_ticker_from_isin_code(
                event.emitted_asset
            )

    return events
