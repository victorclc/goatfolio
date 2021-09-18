import datetime
from typing import Protocol, Optional, List

from domain.models.performance import CandleData


class MarketHistoryRepository(Protocol):
    def find_by_ticker_and_date(
        self, ticker: str, _date: datetime.date
    ) -> Optional[CandleData]:
        """Gets CandleData from given ticker and date or None if nothing is found."""

    def find_by_ticker_from_date(self, ticker: str, from_date: datetime.date) -> Optional[List[CandleData]]:
        """Finds all CandlaDate from given ticker from this from_date"""

    def batch_get_by_tickers_and_date(
        self, tickers: List[str], _date: datetime.date
    ) -> Optional[List[CandleData]]:
        """Finds CandlaDate for each ticker and _date"""
