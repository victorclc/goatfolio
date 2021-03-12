import traceback
from datetime import datetime, date
from decimal import Decimal
from functools import reduce
from itertools import groupby
from typing import List

from dateutil.relativedelta import relativedelta

from adapters import InvestmentRepository, MarketData, PortfolioRepository
from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment
from goatcommons.utils import JsonUtils, DatetimeUtils
from models import OLDStockPosition, OLDPortfolio, PortfolioStock, StockMonthRentability, Portfolio, StockConsolidated, \
    StockPosition


class StockPerformance:
    def __init__(self, investments: List[StockInvestment]):
        self.market_data = MarketData()
        self.investments = sorted(investments, key=lambda i: i.date)
        self.investments_by_month = self._consolidate_investments_by_month()
        self.ticker = self.investments[0].ticker
        self.initial_date = self.investments[0].date
        self.end_date = datetime.now() if self.current_stocks_amount() > 0 else self.investments[-1].date

    def today_variation(self):
        position = OLDStockPosition()
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
        position = OLDStockPosition()
        prev_month_total = Decimal(0)
        performance_history = []
        current_price = None

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
                current_price = month_history.close
                rentability = (month_total * 100 / (prev_month_total + month_invested) - 100).quantize(Decimal('0.0'))
                prev_month_total = month_total
                print(self.ticker, proc_date)
                performance_history.append(
                    {'month_total': month_total, 'rentability': rentability, 'date': int(proc_date.timestamp())})

            proc_date = proc_date + relativedelta(months=1)

        return {'ticker': self.ticker, 'current_price': current_price, 'initial_date': self.initial_date,
                'position': position.to_dict(),
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


class PerformanceCore:
    def __init__(self):
        self.investment_repo = InvestmentRepository()
        self.portfolio_repo = PortfolioRepository()
        self.market_data = MarketData()

    def calculate_portfolio_performance(self, subject):
        assert subject
        portfolio = self.portfolio_repo.find(subject).to_dict()

        for stock in portfolio['stocks']:
            if stock['position']['amount'] > 0:
                stock['current_price'] = MarketData().ticker_intraday_date(stock['ticker']).price
            stock.pop('performance_history')
        print(portfolio)

        return portfolio['stocks']

    def calculate_today_variation(self, subject):
        assert subject
        variations = []
        for _type, stock_investments in groupby(
                sorted(self.investment_repo.find_by_subject(subject), key=lambda i: i.type),
                key=lambda i: i.type):
            if _type == InvestmentsType.STOCK:
                for _ticker, investments in groupby(sorted(stock_investments, key=lambda i: i.ticker),
                                                    key=lambda i: i.ticker):
                    investments = list(investments)
                    variations.append(StockPerformance(investments).today_variation())
        return {'today_variation': sum(variations)}

    def consolidate_portfolio_l(self, subject, investments: List[StockInvestment]):
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)

        for investment in investments:
            print(f'Processing investment: {investment}')
            # if investment.ticker != 'BIDI11':
            #     continue
            try:
                portfolio.initial_date = min(investment.date, portfolio.initial_date)

                if investment.type == InvestmentsType.STOCK:
                    self.consolidate_stock(portfolio.stocks, investment)
            except Exception as ex:
                print(f'DEU RUIM {investment.ticker}')
                print(f'CAUGHT EXCEPTION {ex}')
                traceback.print_exc()

        self.portfolio_repo.save(portfolio)

    def consolidate_portfolio(self, subject, investment: StockInvestment):
        """
            Method responsible to include a new investment or investment edit/delete and consolidate the information
             for faster consumption on a later time
        """
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)
        portfolio.initial_date = min(investment.date, portfolio.initial_date)

        if investment.type == InvestmentsType.STOCK:
            self.consolidate_stock(portfolio.stocks, investment)

        self.portfolio_repo.save(portfolio)

    def consolidate_stock(self, stocks: List[StockConsolidated], investment: StockInvestment):
        stocks_dict = {s.ticker: s for s in stocks}
        if investment.ticker in stocks_dict:
            stock_consolidated = stocks_dict[investment.ticker]
        else:
            stock_consolidated = StockConsolidated(ticker=investment.ticker)
            stocks.append(stock_consolidated)
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, investment.date)
        stock_consolidated.add_investment(investment)

        self.consolidate_stock_history(stock_consolidated.history, investment)

    def consolidate_stock_history(self, history: List[StockPosition], investment: StockInvestment):
        month_datetime = DatetimeUtils.month_first_day_datetime(investment.date)
        month_timestamp = int(month_datetime.timestamp())

        history_dict = {int(h.date.timestamp()): h for h in history}
        amount = investment.amount if investment.operation == OperationType.BUY else -1 * investment.amount

        if month_timestamp not in history_dict:
            candle = self.market_data.ticker_month_data(investment.ticker, investment.date)
            prev_month_timestamp = int(
                DatetimeUtils.month_first_day_datetime(investment.date - relativedelta(months=1)).timestamp())

            position = StockPosition(date=month_datetime, open_price=candle.open, close_price=candle.close)
            history.append(position)
            history_dict[month_timestamp] = position

            self._fix_history_gap(history, history_dict, investment.ticker)

            if prev_month_timestamp in history_dict:
                position.amount = position.amount + history_dict[prev_month_timestamp].amount

        for timestamp in list(filter(lambda d: d >= month_timestamp, history_dict.keys())):
            print(f"Updating history in timestamp: {timestamp}")
            history_dict[timestamp].amount = history_dict[timestamp].amount + amount

    def _fix_history_gap(self, history, history_dict,  ticker):
        timestamps = list(history_dict.keys())
        if len(timestamps) > 1:
            timestamps.sort()
            prev = datetime.fromtimestamp(timestamps[0])
            proc = prev + relativedelta(months=1)
            last = datetime.fromtimestamp(timestamps[-1])

            while proc <= last:
                print(f"PROC: {proc}")
                proc_timestamp = int(proc.timestamp())
                if proc_timestamp not in timestamps:
                    print(f'fix gap: {proc}')
                    candle = self.market_data.ticker_month_data(ticker, proc)
                    position = StockPosition(date=proc, open_price=candle.open, close_price=candle.close,
                                             amount=history_dict[int(prev.timestamp())].amount)
                    history.append(position)
                    history_dict[proc_timestamp] = position
                prev = proc
                proc = proc + relativedelta(months=1)

# import logging
#
# logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    core = PerformanceCore()
    # print(JsonUtils.dump(core.calculate_portfolio_performance('440b0d96-395d-48bd-aaf2-58dbf7e68274')))
    # inv = StockInvestment(**{'amount': Decimal('10'), 'price': Decimal('61.68'), 'ticker': 'ARZZ3', 'operation': 'BUY',
    #                          'date': datetime(2019, 9, 20, 20, 0), 'type': 'STOCK',
    #                          'broker': '308 - CLEAR CORRETORA - GRUPO XP', 'external_system': 'CEI',
    #                          'subject': '440b0d96-395d-48bd-aaf2-58dbf7e68274', 'id': 'CEIARZZ315803424001061681',
    #                          'costs': Decimal('0')})
    # print(core.calculate_portfolio_performance('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    investments = InvestmentRepository().find_by_subject_mocked('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    core.consolidate_portfolio_l('440b0d96-395d-48bd-aaf2-58dbf7e68274', investments)
    # for inv in investments:
    #     if inv.ticker != 'BIDI11':
    #         continue
    #     print(f"Processing inv: {inv}")
    #     try:
    #         core.consolidate_portfolio('440b0d96-395d-48bd-aaf2-58dbf7e68274', inv)
    #     except Exception as ex:
    #         print(f'{inv.ticker} EXCEPTION: {ex}')

# 1580342400
