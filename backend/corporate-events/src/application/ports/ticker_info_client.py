import abc

from application.enums.ticker_type import TickerType


class TickerInfoClient(abc.ABC):
    @abc.abstractmethod
    def get_ticker_code_type(self, ticker_code) -> TickerType:
        ...
