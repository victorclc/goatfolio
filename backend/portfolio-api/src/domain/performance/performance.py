from dataclasses import dataclass, field
import datetime as dt
from decimal import Decimal
from typing import Optional, List


@dataclass
class PortfolioPosition:
    date: dt.date
    invested_value: Decimal = field(default_factory=lambda: Decimal(0))
    gross_value: Decimal = field(default_factory=lambda: Decimal(0))

    def to_json(self):
        return {**self.__dict__, "date": self.date.strftime("%Y%m%d")}


@dataclass
class TickerVariation:
    ticker: str
    variation: Decimal
    last_price: Decimal

    def to_json(self):
        return self.__dict__


@dataclass
class PerformanceSummary:
    invested_amount: Decimal = field(default_factory=lambda: Decimal(0))
    gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    day_variation: Decimal = field(default_factory=lambda: Decimal(0))
    month_variation: Decimal = field(default_factory=lambda: Decimal(0))
    ticker_variation: List[TickerVariation] = field(default_factory=list)

    def __add__(self, other):
        invested_amount = self.invested_amount + other.invested_amount
        gross_amount = self.gross_amount + other.gross_amount
        day_variation = self.day_variation + other.day_variation
        month_variation = self.month_variation + other.month_variation
        ticker_variation = self.ticker_variation + other.ticker_variation

        return invested_amount(
            invested_amount,
            gross_amount,
            day_variation,
            month_variation,
            ticker_variation,
        )

    def to_json(self):
        return {
            **self.__dict__,
            "ticker_variation": [h.to_json() for h in self.ticker_variation],
        }


@dataclass
class TickerConsolidatedHistory:
    history: list

    def to_dict(self):
        return {"history": [h.to_json() for h in self.history]}


@dataclass
class PortfolioList:
    stock_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    reit_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    bdr_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))

    stocks: list = field(default_factory=list)
    reits: list = field(default_factory=list)
    bdrs: list = field(default_factory=list)

    # TODO change to benchmark?
    ibov_history: list = field(default_factory=list)

    def to_dict(self):
        return {
            **self.__dict__,
            "stocks": [s.to_json() for s in self.stocks],
            "reits": [r.to_json() for r in self.reits],
            "bdrs": [b.to_json() for b in self.bdrs],
            "ibov_history": [i.to_json() for i in self.ibov_history],
        }


@dataclass
class CandleData:
    ticker: str
    candle_date: dt.date
    average_price: Decimal
    close_price: Decimal
    company_name: str
    isin_code: str
    open_price: Decimal
    volume: Decimal
    max_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None

    def __post_init__(self):
        if isinstance(self.candle_date, str):
            self.candle_date = dt.datetime.strptime(
                str(self.candle_date), "%Y%m%d"
            ).date()


@dataclass
class BenchmarkPosition:
    date: dt.date
    open: Decimal
    close: Decimal

    def to_dict(self):
        return {**self.__dict__, "date": self.date.strftime("%Y%m%d")}


@dataclass
class StockConsolidatedPosition:
    date: dt.date
    gross_value: Decimal
    invested_value: Decimal
    variation_perc: Decimal

    def to_dict(self):
        return {**self.__dict__, "date": self.date.strftime("%Y%m%d")}
