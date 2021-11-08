from typing import Protocol, List, Dict

from domain.performance.intraday_info import IntradayInfo


class StockIntradayClient(Protocol):
    def get_intraday_info(self, ticker: str) -> IntradayInfo:
        """Fetch the IntradayInfo of the ticker parameter."""

    def batch_get_intraday_info(self, tickers: List[str]) -> Dict[str, IntradayInfo]:
        """Fetch all tickers IntradayInfo and return in a Dict[ticker, IntradayInfo]"""
