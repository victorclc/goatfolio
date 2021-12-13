from typing_extensions import Protocol


class TickerInfoClient(Protocol):
    def is_ticker_valid(self, ticker) -> bool:
        ...
