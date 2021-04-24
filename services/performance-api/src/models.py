from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment


@dataclass
class Portfolio:
    subject: str
    initial_date: datetime = datetime(datetime.max.year, datetime.max.month, datetime.max.day, tzinfo=timezone.utc)
    stocks: list = field(default_factory=list)  # todo list type hint

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date), tz=timezone.utc)
        self.stocks = [StockConsolidated(**s) for s in self.stocks]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'stocks': [s.to_dict() for s in self.stocks]}


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
    ticker: str
    alias_ticker: str = ''
    initial_date: datetime = datetime(datetime.max.year, datetime.max.month, datetime.max.day, tzinfo=timezone.utc)
    history: list = field(default_factory=list)
    current_stock_price: Decimal = field(default_factory=lambda: Decimal(0))
    current_day_change_percent: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date), tz=timezone.utc)
        self.history = [StockPosition(**h) for h in self.history]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'history': sorted([h.to_dict() for h in self.history], key=lambda h: h['date'])}


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

    ibov_history: list

    def to_dict(self):
        return {**self.__dict__, 'stocks': [s.to_dict() for s in self.stocks],
                'reits': [r.to_dict() for r in self.reits], 'bdrs': [b.to_dict() for b in self.bdrs],
                'ibov_history': [i.to_dict() for i in self.ibov_history]}


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
    max_price: Decimal = None
    min_price: Decimal = None

    def __post_init__(self):
        if not isinstance(self.candle_date, datetime):
            tmp_date = datetime.strptime(self.candle_date, '%Y%m%d')
            self.candle_date = datetime(tmp_date.year, tmp_date.month, tmp_date.day, tzinfo=timezone.utc)
