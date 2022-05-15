import datetime
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict

from domain.common.investments import StockDividend
from domain.common.portfolio_item import PortfolioItem


@dataclass
class CashDividendPosition:
    date: datetime.date
    total: Decimal = Decimal(0)
    stocks: Dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.datetime.strptime(self.date, "%Y%m%d").date()

    def add_dividend(self, dividend: StockDividend):
        self.total += dividend.amount
        if dividend.ticker in self.stocks:
            self.stocks[dividend.ticker] += dividend.amount
        else:
            self.stocks[dividend.ticker] = dividend.amount

    def to_dict(self):
        return {
            **self.__dict__,
            "date": self.date.strftime("%Y%m%d")
        }


@dataclass
class CashDividendsSummary(PortfolioItem):
    history: List[CashDividendPosition] = field(default_factory=list)
    _history_map: Dict[datetime.date, CashDividendPosition] = field(init=False, repr=False)

    def __post_init__(self):
        if all(isinstance(h, dict) for h in self.history):
            self.history = [CashDividendPosition(**c) for c in self.history]
        self._history_map = {c.date: c for c in self.history}

    def add_dividend(self, dividend: StockDividend):
        month_start = dividend.date.replace(day=1)
        position = self.get_position_for_date(month_start)
        position.add_dividend(dividend)

    def get_position_for_date(self, date: datetime.date):
        if date in self._history_map:
            return self._history_map[date]
        return self.create_position(date)

    def create_position(self, date: datetime.date):
        position = CashDividendPosition(date)
        self.history.append(position)
        self._history_map[date] = position
        return position

    @property
    def sk(self) -> str:
        return "CASH_DIVIDENDS#"

    def to_json(self):
        return {
            **super().to_json(),
            "history": [h.to_dict() for h in self.history]
        }
