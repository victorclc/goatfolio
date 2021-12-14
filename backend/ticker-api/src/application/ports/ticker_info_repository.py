import abc
from typing import List

from application.models.ticker_info import TickerInfo


class TickerInfoRepository(abc.ABC):
    @abc.abstractmethod
    def get_isin_code_from_ticker(self, ticker: str) -> str:
        ...

    @abc.abstractmethod
    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        ...

    @abc.abstractmethod
    def find_by_code(self, code: str) -> List[TickerInfo]:
        ...
