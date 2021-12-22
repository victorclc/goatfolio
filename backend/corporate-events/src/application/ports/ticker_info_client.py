import abc

from application.enums.ticker_type import TickerType


class TickerInfoClient(abc.ABC):
    @abc.abstractmethod
    def get_ticker_code_type(self, ticker_code) -> TickerType:
        ...

    @abc.abstractmethod
    def get_isin_code_from_ticker(self, ticker: str) -> str:
        """Returns the isin code of a ticker"""

    @abc.abstractmethod
    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        """Returns the Ticker corresponding a isin code"""

