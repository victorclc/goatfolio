import datetime
from typing import Protocol

from domain.performance.ticker_transformation import TickerTransformation


class TickerTransformationClient(Protocol):
    def get_ticker_transformation(
        self, ticker: str, date: datetime.date
    ) -> TickerTransformation:
        """Gets the ticker transformation of the date period"""
