from typing import Protocol


class TickerInfoClient(Protocol):
    def is_ticker_valid(self, ticker) -> bool:
        ...
