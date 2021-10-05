from abc import ABC
from dataclasses import dataclass, field
import datetime as dt
from decimal import Decimal

DATE_FORMAT = "%Y%m%d"


@dataclass
class InvestmentPositionSummary(ABC):
    date: dt.date
    invested_value: Decimal = field(default_factory=lambda: Decimal(0))
    bought_value: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = dt.datetime.strptime(self.date, DATE_FORMAT).date()

    def to_dict(self) -> dict:
        ret = {**self.__dict__, "date": self.date.strftime(DATE_FORMAT)}
        if not self.invested_value:
            ret.pop("invested_value")
        if not self.bought_value:
            ret.pop("bought_value")
        return ret


@dataclass
class StockPositionSummary(InvestmentPositionSummary):
    amount: Decimal = field(default_factory=lambda: Decimal(0))
    average_price: Decimal = field(default_factory=lambda: Decimal(0))

    def to_dict(self) -> dict:
        ret = {**super().to_dict()}
        if not self.average_price:
            ret.pop("average_price")
        return ret
