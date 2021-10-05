from typing import Protocol


class TickerInfoClient(Protocol):
    def get_isin_code_from_ticker(self, ticker: str) -> str:
        """Returns the isin code of a ticker"""

    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        """Returns the Ticker corresponding a isin code"""
