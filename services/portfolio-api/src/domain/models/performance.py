from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from domain.models.investment_summary import StockSummary
import domain.utils as utils


@dataclass
class PortfolioPosition:
    date: datetime
    invested_value: Decimal = field(default_factory=lambda: Decimal(0))
    gross_value: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date), tz=timezone.utc)  # type: ignore

    def to_dict(self):
        return {**self.__dict__, "date": int(self.date.timestamp())}


@dataclass
class PortfolioSummary:
    invested_amount: Decimal = field(default_factory=lambda: Decimal(0))
    gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    day_variation: Decimal = field(default_factory=lambda: Decimal(0))
    month_variation: Decimal = field(default_factory=lambda: Decimal(0))
    stocks_variation: list = field(default_factory=list)

    def to_dict(self):
        return {
            **self.__dict__,
            "stocks_variation": [h.to_dict() for h in self.stocks_variation],
        }

    def consolidate_stock_summary(
        self,
        stock_summary: StockSummary,
        latest_price: Decimal,
        yesterday_price: Decimal,
        prev_month_price: Decimal,
    ):
        s_gross_amount = stock_summary.latest_position.amount * latest_price
        self.gross_amount += s_gross_amount
        self.month_variation += s_gross_amount

        self.day_variation += stock_summary.latest_position.amount * (
            latest_price - yesterday_price
        )
        self.invested_amount += stock_summary.latest_position.invested_value

        if stock_summary.latest_position.date < utils.current_month_start():
            self.month_variation -= (
                    stock_summary.latest_position.amount * prev_month_price
            )
        elif (
            stock_summary.has_active_previous_position()
        ):
            self.month_variation -= (
                stock_summary.previous_position.amount * prev_month_price
            )

        if utils.is_on_same_year_and_month(
            stock_summary.latest_position.date, utils.current_month_start()
        ):
            self.month_variation -= stock_summary.latest_position.bought_value

    def add_stock_variation(self, ticker: str, change: Decimal, price: Decimal):
        self.stocks_variation.append(StockVariation(ticker, change, price))


@dataclass
class StockVariation:
    ticker: str
    variation: Decimal
    last_price: Decimal

    def to_dict(self):
        return self.__dict__


@dataclass
class PortfolioHistory:
    history: list
    ibov_history: list

    def to_dict(self):
        return {
            "history": [h.to_dict() for h in self.history],
            "ibov_history": [h.to_dict() for h in self.ibov_history],
        }


@dataclass
class TickerConsolidatedHistory:
    history: list

    def to_dict(self):
        return {"history": [h.to_dict() for h in self.history]}


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
            "stocks": [s.to_dict() for s in self.stocks],
            "reits": [r.to_dict() for r in self.reits],
            "bdrs": [b.to_dict() for b in self.bdrs],
            "ibov_history": [i.to_dict() for i in self.ibov_history],
        }


@dataclass
class StockSummary:
    ticker: str
    alias_ticker: str
    amount: Decimal
    average_price: Decimal
    invested_amount: Decimal
    current_price: Decimal
    gross_amount: Decimal

    def to_dict(self):
        return self.__dict__


@dataclass
class CandleData:
    ticker: str
    candle_date: datetime
    average_price: Decimal
    close_price: Decimal
    company_name: str
    isin_code: str
    open_price: Decimal
    volume: Decimal
    max_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None

    def __post_init__(self):
        if not isinstance(self.candle_date, datetime):
            tmp_date = datetime.strptime(self.candle_date, "%Y%m%d")  # type: ignore
            self.candle_date = datetime(
                tmp_date.year, tmp_date.month, tmp_date.day, tzinfo=timezone.utc
            )


@dataclass
class BenchmarkPosition:
    date: datetime
    open: Decimal
    close: Decimal

    def to_dict(self):
        return {**self.__dict__, "date": int(self.date.timestamp())}


@dataclass
class StockConsolidatedPosition:
    date: datetime
    gross_value: Decimal
    invested_value: Decimal
    variation_perc: Decimal

    def to_dict(self):
        return {**self.__dict__, "date": int(self.date.timestamp())}
