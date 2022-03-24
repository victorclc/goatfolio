from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import List

from application.models.user import User


@dataclass
class TickerVariation:
    ticker: str
    variation: Decimal
    last_price: Decimal

    def __post_init__(self):
        self.variation = Decimal(self.variation).quantize(Decimal("0.01"))
        self.last_price = Decimal(self.last_price).quantize(Decimal("0.01"))

    def to_dict(self):
        return self.__dict__


@dataclass
class PerformancePercentageSummary:
    day_variation_perc: Decimal
    month_variation_perc: Decimal
    ticker_variation: List[TickerVariation]

    def __post_init__(self):
        self.day_variation_perc = Decimal(self.day_variation_perc).quantize(Decimal("0.01"))
        self.month_variation_perc = Decimal(self.month_variation_perc).quantize(Decimal("0.01"))
        self.ticker_variation = [TickerVariation(**tv) for tv in self.ticker_variation]

    def to_dict(self):
        return {
            **self.__dict__,
            "ticker_variation": [h.to_dict() for h in self.ticker_variation],
        }


@dataclass
class UserRentability:
    user: User
    summary: PerformancePercentageSummary

    def to_dict(self):
        return {
            "user": asdict(self.user),
            "summary": self.summary.to_dict()
        }
