from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class TickerVariation:
    ticker: str
    variation: Decimal
    last_price: Decimal

    def to_dict(self):
        return self.__dict__


@dataclass
class PerformanceSummary:
    invested_amount: Decimal
    gross_amount: Decimal
    day_variation: Decimal
    month_variation: Decimal
    ticker_variation: List[TickerVariation]

    def __post_init__(self):
        self.invested_amount = Decimal(self.invested_amount).quantize(Decimal("0.01"))
        self.gross_amount = Decimal(self.gross_amount).quantize(Decimal("0.01"))
        self.day_variation = Decimal(self.day_variation).quantize(Decimal("0.01"))
        self.month_variation = Decimal(self.month_variation).quantize(Decimal("0.01"))
        self.ticker_variation = [TickerVariation(**tv) for tv in self.ticker_variation]

    def to_dict(self):
        return {
            **self.__dict__,
            "ticker_variation": [h.to_dict() for h in self.ticker_variation],
        }
