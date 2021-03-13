from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment
from goatcommons.utils import DatetimeUtils


@dataclass
class Portfolio:
    subject: str
    invested_amount: Decimal = field(default_factory=lambda: Decimal(0))
    stock_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    reit_gross_amount: Decimal = field(default_factory=lambda: Decimal(0))
    initial_date: datetime = datetime.max
    stocks: list = field(default_factory=list)  # todo list type hint
    reits: list = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.initial_date, datetime):
            self.initial_date = datetime.fromtimestamp(float(self.initial_date))
        self.stocks = [StockConsolidated(**s) for s in self.stocks]
        self.reits = [StockConsolidated(**s) for s in self.reits]

    def to_dict(self):
        return {**self.__dict__, 'initial_date': int(self.initial_date.timestamp()),
                'stocks': [s.to_dict() for s in self.stocks], 'reits': [s.to_dict() for s in self.reits]}


@dataclass
class StockConsolidated:
    ticker: str
    initial_date: datetime = datetime.max
    history: list = field(default_factory=list)
    current_stock_price: Decimal = field(default_factory=lambda: Decimal(0))
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

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date))

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


class OLDStockPosition:
    def __init__(self, bought_amount=None, sold_amount=None, total_spend=None, total_sold=None, **kwargs):
        self.bought_amount = bought_amount if bought_amount else Decimal(0)
        self.sold_amount = sold_amount if sold_amount else Decimal(0)
        self.total_spend = total_spend if total_spend else Decimal(0)
        self.total_sold = total_sold if total_sold else Decimal(0)

    @property
    def amount(self):
        return self.bought_amount - self.sold_amount

    @property
    def average_price(self):
        if self.bought_amount > 0:
            return (self.total_spend / self.bought_amount).quantize(Decimal('0.01'))
        return Decimal('0.00')

    @property
    def current_invested(self):
        return self.amount * self.average_price

    def add_investment(self, investment: StockInvestment):
        if investment.operation == OperationType.BUY:
            self.bought_amount = self.bought_amount + investment.amount
            self.total_spend = self.total_spend + investment.amount * investment.price
        else:
            self.sold_amount = self.sold_amount + investment.amount
            self.total_sold = self.total_sold + investment.amount * investment.price

    def to_dict(self):
        return {**self.__dict__, 'amount': self.amount, 'average_price': self.average_price,
                'current_invested': self.current_invested}


class OLDPortfolio:
    def __init__(self, subject, initial_date=datetime.max, stocks=None):
        if stocks is None:
            stocks = []
        self.subject = subject
        self.initial_date = initial_date
        self.stocks = {s.ticker: s for s in stocks}

    def add_investment(self, investment):
        inv_datetime = int(investment.date.timestamp())
        if not self.initial_date or self.initial_date > inv_datetime:
            self.initial_date = inv_datetime

        if investment.type == InvestmentsType.STOCK:
            if investment.ticker not in self.stocks:
                self.stocks[investment.ticker] = PortfolioStock(investment.ticker, inv_datetime, OLDStockPosition(),
                                                                performance_history=StockPerformanceHistory())
            self.stocks[investment.ticker].add_investment(investment=investment)

    @staticmethod
    def from_dict(_dict):
        tmp = list(map(lambda s: PortfolioStock.from_dict(s), _dict['stocks']))
        new_dict = dict(_dict)
        new_dict['stocks'] = tmp
        return OLDPortfolio(**new_dict)

    def to_dict(self):
        return {'subject': self.subject, 'initial_date': self.initial_date,
                'stocks': [s.to_dict() for s in self.stocks.values()]}


class PortfolioStock:
    def __init__(self, ticker, initial_date, position, performance_history, current_price=Decimal(0)):
        self.ticker = ticker
        self.initial_date = int(initial_date)
        self.position = position
        self.current_price = current_price
        self.performance_history = performance_history

    def add_investment(self, investment: StockInvestment):
        inv_datetime = int(investment.date.timestamp())
        if not self.initial_date or self.initial_date > inv_datetime:
            self.initial_date = inv_datetime
        self.position.add_investment(investment=investment)
        self.performance_history.add_investment(investment=investment)

    @staticmethod
    def from_dict(_dict):
        new_dict = dict(_dict)
        new_dict['position'] = OLDStockPosition(**_dict['position'])
        if 'performance_history' in _dict:
            new_dict['performance_history'] = StockPerformanceHistory.from_dict(_dict['performance_history'])
        else:
            new_dict['performance_history'] = StockPerformanceHistory()
        return PortfolioStock(**new_dict)

    def to_dict(self):
        return {
            'ticker': self.ticker,
            'initial_date': self.initial_date,
            'current_price': self.current_price,
            'position': self.position.to_dict(),
            'performance_history': self.performance_history.to_dict()
        }


class StockMonthRentability:
    def __init__(self, date, position: OLDStockPosition, price=Decimal(0)):
        self.date = date
        self.position = position
        self.price = price

    @staticmethod
    def from_dict(_dict):
        new_dict = dict(_dict)
        new_dict['position'] = OLDStockPosition(**_dict['position'])
        return StockMonthRentability(**new_dict)

    def to_dict(self):
        return {'date': self.date, 'price': self.price, 'position': self.position.to_dict()}


class StockPerformanceHistory:
    def __init__(self, history=None):
        if history is None:
            history = []
        self.history = {h.date: h for h in history}

    def add_investment(self, investment: StockInvestment):
        month_timestamp = int(DatetimeUtils.month_first_day_datetime(investment.date).timestamp())
        if month_timestamp not in self.history:
            from adapters import MarketData
            candle = MarketData().ticker_month_data(investment.ticker, investment.date)
            prev_timestamp = int(
                DatetimeUtils.month_first_day_datetime(investment.date - relativedelta(months=1)).timestamp())
            if prev_timestamp in self.history:
                position = OLDStockPosition(**self.history[prev_timestamp].position.to_dict())
            else:
                position = OLDStockPosition()
            self.history[month_timestamp] = StockMonthRentability(date=month_timestamp, position=position,
                                                                  price=candle.close)
        for timestamp in list(filter(lambda d: d >= month_timestamp, self.history.keys())):
            print(f"atualizando posicao date: {timestamp}")
            self.history[timestamp].position.add_investment(investment)
        self.fill_gaps(investment.ticker)

    def fill_gaps(self, ticker):
        timestamps = list(self.history.keys())
        if len(timestamps) == 1:
            return
        timestamps.sort()
        print(timestamps)
        prev = datetime.fromtimestamp(timestamps[0])
        proc = prev + relativedelta(months=1)
        last = datetime.fromtimestamp(timestamps[-1])

        while proc < last:
            proc_timestamp = int(proc.timestamp())
            if proc_timestamp not in timestamps:
                print(f'fix gap: {proc}')
                from adapters import MarketData
                candle = MarketData().ticker_month_data(ticker, proc)
                position = OLDStockPosition(**self.history[int(prev.timestamp())].position.to_dict())
                self.history[proc_timestamp] = StockMonthRentability(date=proc_timestamp, position=position,
                                                                     price=candle.close)
            proc = proc + relativedelta(months=1)

    @staticmethod
    def from_dict(_dict):
        return StockPerformanceHistory(list(map(lambda s: StockMonthRentability.from_dict(s), _dict)))

    def to_dict(self):
        return [s.to_dict() for s in self.history.values()]
