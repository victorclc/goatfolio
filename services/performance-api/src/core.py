from dataclasses import dataclass, asdict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from functools import reduce
from itertools import groupby
from typing import List

from adapters import InvestmentRepository, MarketData
from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment


class StockPerformance:
    def __init__(self, investments: List[StockInvestment]):
        self.market_data = MarketData()
        self.investments = sorted(investments, key=lambda i: i.date)
        self.investments_by_month = self._consolidate_investments_by_month()
        self.ticker = self.investments[0].ticker
        self.initial_date = self.investments[0].date
        self.end_date = datetime.now() if self.current_stocks_amount() > 0 else self.investments[-1].date

    def performance(self):
        history = self.market_data.ticker_monthly_data(self.ticker, self.initial_date)
        position = self.StockPosition()
        prev_month_total = Decimal(0)
        performance_history = []

        proc_date = datetime(self.initial_date.year, self.initial_date.month, 1)
        while proc_date <= self.end_date:
            month_investments = self._month_investments(proc_date.date())
            month_history = history.pop()
            month_invested = Decimal(0)

            if month_investments:
                for inv in month_investments:
                    position.add_investment(inv)
                    month_invested = inv.amount * inv.price

            month_total = month_history.close * position.amount
            rentability = (month_total * 100 / (prev_month_total + month_invested) - 100).quantize(Decimal('0.0'))
            prev_month_total = month_total
            proc_date = proc_date + relativedelta(months=1)
            performance_history.append(
                {'month_total': month_total, 'rentability': rentability, 'date': proc_date.strftime('%Y%m%d')})

        return {'ticker': self.ticker, 'initial_data': self.initial_date, 'position': position.to_dict(),
                "performance_history": performance_history}

    def _month_investments(self, date_inv):
        key = date_inv.strftime('%Y%m')
        if key in self.investments_by_month:
            return self.investments_by_month[key]
        return None

    def _consolidate_investments_by_month(self):
        consolidated = {}
        for k, v in groupby(self.investments, key=lambda i: date(i.date.year, i.date.month, 1)):
            consolidated[k.strftime('%Y%m')] = list(v)
        return consolidated

    def current_stocks_amount(self):
        return reduce(lambda p, i: p + i.amount if i.operation == OperationType.BUY else p + (-1 * i.amount),
                      self.investments, 0)

    class StockPosition:
        def __init__(self):
            self.bought_amount = Decimal(0)
            self.sold_amount = Decimal(0)
            self.total_spend = Decimal(0)
            self.total_sold = Decimal(0)

        @property
        def amount(self):
            return self.bought_amount - self.sold_amount

        @property
        def average_price(self):
            return (self.total_spend / self.bought_amount).quantize(Decimal('0.01'))

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


class PerformanceCore:
    def __init__(self):
        self.repo = InvestmentRepository()

    def calculate_portfolio_performance(self, subject):
        performances = []
        for _type, stock_investments in groupby(sorted(self.repo.find_by_subject(subject), key=lambda i: i.type),
                                                key=lambda i: i.type):
            if _type == InvestmentsType.STOCK:
                for _ticker, investments in groupby(sorted(stock_investments, key=lambda i: i.ticker),
                                                    key=lambda i: i.ticker):
                    investments = list(investments)
                    performances.append(StockPerformance(investments).performance())

        return performances


if __name__ == '__main__':
    core = PerformanceCore()
    print(core.calculate_portfolio_performance('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
