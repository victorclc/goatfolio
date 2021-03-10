from datetime import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment
from goatcommons.utils import DatetimeUtils


class StockPosition:
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
        return self.total_spend - self.total_sold

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


class Portfolio:
    def __init__(self, subject, initial_date=None, stocks=None):
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
                self.stocks[investment.ticker] = PortfolioStock(investment.ticker, inv_datetime, StockPosition(),
                                                                performance_history=StockPerformanceHistory())
            self.stocks[investment.ticker].add_investment(investment=investment)

    @staticmethod
    def from_dict(_dict):
        tmp = list(map(lambda s: PortfolioStock.from_dict(s), _dict['stocks']))
        new_dict = dict(_dict)
        new_dict['stocks'] = tmp
        return Portfolio(**new_dict)

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
        new_dict['position'] = StockPosition(**_dict['position'])
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
    def __init__(self, date, position: StockPosition, price=Decimal(0)):
        self.date = date
        self.position = position
        self.price = price

    @staticmethod
    def from_dict(_dict):
        new_dict = dict(_dict)
        new_dict['position'] = StockPosition(**_dict['position'])
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
                position = StockPosition(**self.history[prev_timestamp].position.to_dict())
            else:
                position = StockPosition()
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
                position = StockPosition(**self.history[int(prev.timestamp())].position.to_dict())
                self.history[proc_timestamp] = StockMonthRentability(date=proc_timestamp, position=position,
                                                                     price=candle.close)
            proc = proc + relativedelta(months=1)

    @staticmethod
    def from_dict(_dict):
        return StockPerformanceHistory(list(map(lambda s: StockMonthRentability.from_dict(s), _dict)))

    def to_dict(self):
        return [s.to_dict() for s in self.history.values()]
