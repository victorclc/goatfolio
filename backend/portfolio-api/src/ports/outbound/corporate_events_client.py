import datetime
from typing import Protocol, List

from domain.performance.ticker_transformation import TickerTransformation
from domain.corporate_events.earnings_in_assets_event import EarningsInAssetCorporateEvent


class CorporateEventsClient(Protocol):
    def get_ticker_transformation(
        self, subject: str, ticker: str, date: datetime.date
    ) -> TickerTransformation:
        """Gets the ticker transformation of the date period"""

    def corporate_events_from_date(
        self, subject: str, ticker: str, date: datetime.date
    ) -> List[EarningsInAssetCorporateEvent]:
        """Gets all corporate events of the date period"""
