from dataclasses import dataclass, field
from datetime import datetime
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
    initial_date: datetime = datetime.max
    stocks: list = field(default_factory=list)  # todo list type hint
    reits: list = field(default_factory=list)
    history: list = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date))
        self.stocks = [StockConsolidated(**s) for s in self.stocks]
        self.reits = [StockConsolidated(**s) for s in self.reits]
        self.history = [PortfolioPosition(**p) for p in self.history]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'stocks': [s.to_dict() for s in self.stocks], 'reits': [s.to_dict() for s in self.reits],
                'history': [h.to_dict() for h in self.history]}


@dataclass
class StockConsolidated:
    ticker: str
    initial_date: datetime = datetime.max
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

    def add_investment(self, investment: StockInvestment):
        if investment.operation == OperationType.BUY:
            self.bought_amount = self.bought_amount + investment.amount
            self.total_spend = self.total_spend + investment.amount * investment.price
        else:
            self.sold_amount = self.sold_amount + investment.amount
            self.total_sold = self.total_sold + investment.amount * investment.price

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date))
        self.history = [StockPosition(**h) for h in self.history]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'history': [h.to_dict() for h in self.history]}


@dataclass
class StockPosition:
    date: datetime
    open_price: Decimal
    close_price: Decimal
    amount: Decimal = field(default_factory=lambda: Decimal(0))
    invested_amount: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date))

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


@dataclass
class PortfolioPosition:
    date: datetime
    total_invested: Decimal = field(default_factory=lambda: Decimal(0))
    gross_amount: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date))

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}
