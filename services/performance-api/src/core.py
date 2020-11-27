from datetime import datetime
from functools import reduce
from itertools import groupby
from typing import List

from adapters import InvestmentRepository
from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment


class StockPerformance:
    def __init__(self, investments: List[StockInvestment]):
        self.investments = sorted(investments, key=lambda i: i.date)
        self.stock_amount = self._current_stocks_amount()
        self.initial_date = self.investments[0].date
        self.ticker = self.investments[0].ticker
        self.end_date = datetime.now() if self.stock_amount > 0 else self.investments[-1].date

    def performance(self):
        pass

    def _current_stocks_amount(self):
        return reduce(lambda i: i.amount if i.operation is OperationType.BUY else -1 * i.amount, self.investments, 0)


class PerformanceCore:
    def __init__(self):
        self.repo = InvestmentRepository()

    def calculate_portfolio_performance(self, subject):
        performances = []
        for _type, stock_investments in groupby(sorted(self.repo.find_by_subject(subject), key=lambda i: i.type)):
            if _type == InvestmentsType.STOCK:
                for _ticker, investments in groupby(sorted(stock_investments, key=lambda i: i.ticker)):
                    performance = StockPerformance(investments).performance()
                    performances.append(performance)
