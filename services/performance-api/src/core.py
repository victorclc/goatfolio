from datetime import datetime, date
from decimal import Decimal
from functools import reduce
from itertools import groupby
from typing import List

from dateutil.relativedelta import relativedelta

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

    def today_variation(self):
        position = self.StockPosition()
        today = datetime.now()
        t_invested = Decimal(0)
        t_amount = Decimal(0)
        for inv in self.investments:
            if inv.date == today:
                t_invested = t_invested + inv.amount * inv.price * 1 if inv.operation == OperationType.BUY else -1
                t_amount = t_amount + inv.amount * 1 if inv.operation == OperationType.BUY else -1
            position.add_investment(inv)
        if position.amount > 0:
            intra_data = self.market_data.ticker_intraday_date(self.ticker)
            return position.amount * intra_data.price - t_invested - (
                    position.amount - t_amount) * intra_data.prev_close_price
        return Decimal(0)

    def performance(self):
        history = self.market_data.ticker_monthly_data(self.ticker, self.initial_date)
        position = self.StockPosition()
        prev_month_total = Decimal(0)
        performance_history = []

        end_date = datetime(self.end_date.year, self.end_date.month, 1)
        proc_date = datetime(self.initial_date.year, self.initial_date.month, 1)

        while proc_date <= end_date:
            month_investments = self._month_investments(proc_date.date())
            month_invested = Decimal(0)

            if month_investments:
                for inv in month_investments:
                    position.add_investment(inv)
                    month_invested = inv.amount * inv.price

            if end_date - relativedelta(months=12) < proc_date and prev_month_total + month_invested > 0:
                month_history = history.pop()
                month_total = month_history.close * position.amount
                rentability = (month_total * 100 / (prev_month_total + month_invested) - 100).quantize(Decimal('0.0'))
                prev_month_total = month_total
                print(self.ticker, proc_date)
                performance_history.append(
                    {'month_total': month_total, 'rentability': rentability, 'date': int(proc_date.timestamp())})

            proc_date = proc_date + relativedelta(months=1)

        return {'ticker': self.ticker, 'initial_date': self.initial_date, 'position': position.to_dict(),
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


class PerformanceCore:
    def __init__(self):
        self.repo = InvestmentRepository()

    def calculate_portfolio_performance(self, subject):
        assert subject
        performances = []
        for _type, stock_investments in groupby(sorted(self.repo.find_by_subject(subject), key=lambda i: i.type),
                                                key=lambda i: i.type):
            if _type == InvestmentsType.STOCK:
                for _ticker, investments in groupby(sorted(stock_investments, key=lambda i: i.ticker),
                                                    key=lambda i: i.ticker):
                    investments = list(investments)
                    try:
                        performances.append(StockPerformance(investments).performance())
                    except Exception as e:
                        print(e)
                        pass
        return performances

    def calculate_today_variation(self, subject):
        assert subject
        variations = []
        for _type, stock_investments in groupby(sorted(self.repo.find_by_subject(subject), key=lambda i: i.type),
                                                key=lambda i: i.type):
            if _type == InvestmentsType.STOCK:
                for _ticker, investments in groupby(sorted(stock_investments, key=lambda i: i.ticker),
                                                    key=lambda i: i.ticker):
                    investments = list(investments)
                    variations.append(StockPerformance(investments).today_variation())
        return {'today_variation': sum(variations)}


if __name__ == '__main__':
    core = PerformanceCore()
    print(core.calculate_portfolio_performance('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
