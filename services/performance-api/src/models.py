from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment


@dataclass
class Portfolio:
    subject: str
    invested_amount: Decimal = field(default_factory=lambda: Decimal(0))
    stock_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    stock_prev_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    reit_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    reit_prev_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    initial_date: datetime = datetime(datetime.max.year, datetime.max.month, datetime.max.day, tzinfo=timezone.utc)
    stocks: list = field(default_factory=list)  # todo list type hint
    reits: list = field(default_factory=list)
    history: list = field(default_factory=list)
    ibov_history: list = field(default_factory=list)

    @property
    def all_investments(self):
        return self.stocks + self.reits

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date), tz=timezone.utc)
        self.stocks = [StockConsolidated(**s) for s in self.stocks]
        self.reits = [StockConsolidated(**s) for s in self.reits]
        self.history = [PortfolioPosition(**p) for p in self.history]
        self.ibov_history = [StockPosition(**p) for p in self.ibov_history]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'stocks': [s.to_dict() for s in self.stocks], 'reits': [s.to_dict() for s in self.reits],
                'history': [h.to_dict() for h in self.history],
                'ibov_history': [i.to_dict() for i in self.ibov_history]}


@dataclass
class StockConsolidated:
    ticker: str
    alias_ticker: str = ''
    initial_date: datetime = datetime(datetime.max.year, datetime.max.month, datetime.max.day, tzinfo=timezone.utc)
    history: list = field(default_factory=list)
    current_stock_price: Decimal = field(default_factory=lambda: Decimal(0))
    current_day_change_percent: Decimal = field(default_factory=lambda: Decimal(0))
    bought_amount: Decimal = field(default_factory=lambda: Decimal(0))
    sold_amount: Decimal = field(default_factory=lambda: Decimal(0))
    total_spend: Decimal = field(default_factory=lambda: Decimal(0))
    total_sold: Decimal = field(default_factory=lambda: Decimal(0))

    @property
    def current_amount(self):
        return self.bought_amount - self.sold_amount

    @property
    def prev_month_amount(self):
        if self.history:
            now = datetime.now()
            if self.history[-1].date.year == now.year and self.history[-1].date.month == now.month:
                if len(self.history) >= 2:
                    return self.history[-2].amount
            else:
                return self.history[-1].amount
        return Decimal(0)

    @property
    def value_invested_current_month(self):
        if self.history:
            now = datetime.now()
            if self.history[-1].date.year == now.year and self.history[-1].date.month == now.month:
                return self.history[-1].invested_value
        return Decimal(0)

    @property
    def sold_amount_current_month(self):
        if self.history:
            now = datetime.now()
            if self.history[-1].date.year == now.year and self.history[-1].date.month == now.month:
                return self.history[-1].sold_amount
        return Decimal(0)

    @property
    def average_price(self):
        return self.total_spend / self.bought_amount if self.bought_amount != 0 else Decimal(0)

    @property
    def current_invested(self):
        return self.current_amount * self.average_price

    def add_investment(self, investment: StockInvestment):
        if investment.operation in [OperationType.BUY, OperationType.SPLIT, OperationType.INCORP_ADD]:
            self.bought_amount = self.bought_amount + investment.amount
            self.total_spend = self.total_spend + investment.amount * investment.price
        elif investment.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            self.bought_amount = self.bought_amount - investment.amount
        else:
            self.sold_amount = self.sold_amount + investment.amount
            self.total_sold = self.total_sold + investment.amount * investment.price

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date), tz=timezone.utc)
        self.history = [StockPosition(**h) for h in self.history]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'history': sorted([h.to_dict() for h in self.history], key=lambda h: h['date'])}


@dataclass
class StockPosition:
    date: datetime
    open_price: Decimal = field(default_factory=lambda: Decimal(0))
    close_price: Decimal = field(default_factory=lambda: Decimal(0))
    amount: Decimal = field(default_factory=lambda: Decimal(0))
    sold_amount: Decimal = field(default_factory=lambda: Decimal(0))
    bought_amount: Decimal = field(default_factory=lambda: Decimal(0))
    invested_value: Decimal = field(default_factory=lambda: Decimal(0))
    sold_value: Decimal = field(default_factory=lambda: Decimal(0))
    realized_profit: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date), tz=timezone.utc)

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


@dataclass
class PortfolioPosition:
    date: datetime
    total_invested: Decimal = field(default_factory=lambda: Decimal(0))
    gross_amount: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date), tz=timezone.utc)

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


@dataclass
class PortfolioSummary:
    invested_amount: Decimal
    gross_amount: Decimal
    day_variation: Decimal
    month_variation: Decimal
    stocks_variation: list

    def to_dict(self):
        return {**self.__dict__, 'stocks_variation': [h.to_dict() for h in self.stocks_variation]}


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
        return {'history': [h.to_dict() for h in self.history],
                'ibov_history': [h.to_dict() for h in self.ibov_history]}


@dataclass
class TickerConsolidatedHistory:
    history: list

    def to_dict(self):
        return {'history': [h.to_dict() for h in self.history]}


@dataclass
class PortfolioList:
    stock_gross_amount: Decimal
    reit_gross_amount: Decimal
    bdr_gross_amount: Decimal

    stocks: list
    reits: list
    bdrs: list

    def to_dict(self):
        return {**self.__dict__, 'stocks': [s.to_dict() for s in self.stocks],
                'reits': [r.to_dict() for r in self.reits], 'bdrs': [b.to_dict() for b in self.bdrs]}


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
