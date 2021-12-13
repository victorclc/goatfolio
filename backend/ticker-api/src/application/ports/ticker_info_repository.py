import abc


class TickerInfoRepository(abc.ABC):
    @abc.abstractmethod
    def get_isin_code_from_ticker(self, ticker: str) -> str:
        ...

    @abc.abstractmethod
    def get_ticker_from_isin_code(self, isin_code: str) -> str:
        ...
