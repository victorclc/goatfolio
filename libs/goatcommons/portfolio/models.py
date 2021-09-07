from decimal import Decimal
from dataclasses import dataclass, field
from datetime import datetime, timezone

from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment


@dataclass
class Portfolio:
    subject: str
    ticker: str
    initial_date: datetime = datetime(datetime.max.year, datetime.max.month, datetime.max.day, tzinfo=timezone.utc)
    stocks: list = field(default_factory=list)  # todo list type hint

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date), tz=timezone.utc)
        self.stocks = [StockSummary(**s) if not isinstance(s, StockSummary) else s for s in self.stocks]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'stocks': [s.to_dict() for s in self.stocks]}


@dataclass
class StockPositionMonthlySummary:
    date: datetime
    amount: Decimal
    invested_value: Decimal = field(default_factory=lambda: Decimal(0))
    bought_value: Decimal = field(default_factory=lambda: Decimal(0))
    average_price: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if type(self.date) is not datetime:
            self.date = datetime.fromtimestamp(self.date, tz=timezone.utc)

    def to_dict(self):
        ret = {**self.__dict__, 'date': int(self.date.timestamp())}
        if not self.invested_value:
            ret.pop('invested_value')
        if not self.bought_value:
            ret.pop('bought_value')
        if not self.average_price:
            ret.pop('average_price')
        return ret


@dataclass
class StockSummary:
    ticker: str
    latest_position: StockPositionMonthlySummary
    previous_position: StockPositionMonthlySummary = None
    alias_ticker: str = ''

    def __post_init__(self):
        if type(self.latest_position) is not StockPositionMonthlySummary:
            self.latest_position = StockPositionMonthlySummary(**self.latest_position)
        if self.previous_position and type(self.previous_position) is not StockPositionMonthlySummary:
            self.previous_position = StockPositionMonthlySummary(**self.previous_position)

    def to_dict(self):
        ret = {
            **self.__dict__, 'latest_position': self.latest_position.to_dict()
        }
        if self.previous_position:
            ret['previous_position'] = self.previous_position.to_dict()
        return ret


@dataclass
class StockPosition:
    date: datetime
    sold_amount: Decimal = field(default_factory=lambda: Decimal(0))
    bought_amount: Decimal = field(default_factory=lambda: Decimal(0))
    bought_value: Decimal = field(default_factory=lambda: Decimal(0))
    sold_value: Decimal = field(default_factory=lambda: Decimal(0))
    close_price: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if type(self.date) is not datetime:
            self.date = datetime.fromtimestamp(self.date, tz=timezone.utc)

        self.sold_amount = Decimal(self.sold_amount).quantize(Decimal('0.01'))
        self.bought_amount = Decimal(self.bought_amount).quantize(Decimal('0.01'))
        self.bought_value = Decimal(self.bought_value).quantize(Decimal('0.01'))
        self.sold_value = Decimal(self.sold_value).quantize(Decimal('0.01'))

    def __add__(self, other):
        sold_amount = self.sold_amount + other.sold_amount
        bought_amount = self.bought_amount + other.bought_amount
        bought_value = self.bought_value + other.bought_value
        sold_value = self.sold_value + other.sold_value

        return StockPosition(self.date, sold_amount, bought_amount, bought_value, sold_value)

    @staticmethod
    def from_stock_investment(investment: StockInvestment):
        sold_amount = 0
        sold_value = 0
        bought_amount = 0
        bought_value = 0
        date = datetime(investment.date.year, investment.date.month, investment.date.day, tzinfo=timezone.utc)

        if investment.operation == OperationType.BUY:
            bought_amount = investment.amount
            bought_value = investment.amount * investment.price
        elif investment.operation == OperationType.SELL:
            sold_amount = investment.amount
            sold_value = investment.amount * investment.price
        elif investment.operation in [OperationType.SPLIT, OperationType.INCORP_ADD]:
            bought_amount = investment.amount
        elif investment.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            sold_amount = investment.amount
        return StockPosition(date, sold_amount, bought_amount, bought_value, sold_value)

    def add_investment(self, investment):
        sold_amount = 0
        sold_value = 0
        bought_amount = 0
        bought_value = 0

        if investment.operation == OperationType.BUY:
            bought_amount = investment.amount
            bought_value = investment.amount * investment.price
        elif investment.operation == OperationType.SELL:
            sold_amount = investment.amount
            sold_value = investment.amount * investment.price
        elif investment.operation in [OperationType.SPLIT, OperationType.INCORP_ADD]:
            bought_amount = investment.amount
        elif investment.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            sold_amount = investment.amount

        self.sold_amount = self.sold_amount + sold_amount
        self.sold_value = self.sold_value + sold_value
        self.bought_amount = self.bought_amount + bought_amount
        self.bought_value = self.bought_value + bought_value

    def is_empty(self):
        return not self.sold_amount and not self.bought_amount and not self.bought_value and not self.sold_value

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


@dataclass
class StockConsolidated:
    subject: str
    ticker: str
    alias_ticker: str = ''
    initial_date: datetime = datetime(datetime.max.year, datetime.max.month, datetime.max.day, tzinfo=timezone.utc)
    history: list = field(default_factory=list)
    current_stock_price: Decimal = field(default_factory=lambda: Decimal(0))
    current_day_change_percent: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date), tz=timezone.utc)
        self.history = [StockPosition(**h) if not isinstance(h, StockPosition) else h for h in self.history]

    def to_dict(self):
        ret = {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
               'history': sorted([h.to_dict() for h in self.history], key=lambda h: h['date']),
               'alias_ticker': self.alias_ticker or self.ticker}
        ret.pop('current_stock_price')
        ret.pop('current_day_change_percent')
        return ret

    def __add__(self, other):
        initial_date = min(self.initial_date, other.initial_date)
        return StockConsolidated(self.subject, self.alias_ticker, initial_date=initial_date,
                                 history=self.history + other.history)
