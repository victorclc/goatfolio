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
from goatcommons.utils import DatetimeUtils
from models import OLDStockPosition, Portfolio, StockConsolidated, StockPosition, PortfolioPosition


class PerformanceCore:
    def __init__(self):
        self.investment_repo = InvestmentRepository()
        self.portfolio_repo = PortfolioRepository()
        self.market_data = MarketData()

    def calculate_portfolio_performance(self, subject):
        assert subject
        portfolio = self.portfolio_repo.find(subject)

        stock_performance = self._calculate_stocks_performance(portfolio.stocks)
        reit_performance = self._calculate_stocks_performance(portfolio.reits)

        portfolio.stocks, portfolio.stock_gross_amount, portfolio.stock_prev_gross_amount = stock_performance
        portfolio.reits, portfolio.reit_gross_amount, portfolio.reit_prev_gross_amount = reit_performance

        h_dict = {int(h.date.timestamp()): h for h in portfolio.history}
        s_history = [item for sublist in [s.history for s in portfolio.stocks + portfolio.reits] for item in sublist]

        for s_position in s_history:
            s_timestamp = int(s_position.date.timestamp())
            h_dict[s_timestamp].gross_amount = h_dict[
                                                   s_timestamp].gross_amount + s_position.amount * s_position.close_price

        return portfolio

    def _calculate_stocks_performance(self, stocks: List[StockConsolidated]):
        """
            Calculate current position of all stocks, returns a list of stocks without 0 amount positions,
            gross_amount and prev_gross_amount
        """
        gross_amount = Decimal(0)
        prev_gross_amount = Decimal(0)
        zeroed_stocks = []

        for stock in stocks:
            if stock.current_amount > 0:
                data = self.market_data.ticker_intraday_date(stock.ticker)
                gross_amount = gross_amount + stock.current_amount * data.price
                prev_gross_amount = prev_gross_amount + stock.current_amount * data.prev_close_price
                stock.current_stock_price = data.price
                stock.current_day_change_percent = data.change
            else:
                print(f"REMOVING {stock.ticker}")
                zeroed_stocks.append(stock)
        return [stock for stock in stocks if stock not in zeroed_stocks], gross_amount, prev_gross_amount

    def consolidate_portfolio_l(self, subject, investments: List[StockInvestment]):
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)

        for investment in investments:
            print(f'Processing investment: {investment}')
            # if investment.ticker != 'BIDI11':
            #     continue
            try:
                portfolio.initial_date = min(investment.date, portfolio.initial_date)

                if investment.type == InvestmentsType.STOCK:
                    value = investment.amount * investment.price * (
                        -1 if investment.operation == OperationType.SELL else 1)
                    print(f'VALUE: {value}')
                    portfolio.invested_amount = portfolio.invested_amount + value
                    self.consolidate_portfolio_history(portfolio, investment)
                    self.consolidate_stock(portfolio, investment)
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
            value = investment.amount * investment.price * (-1 if investment.operation == OperationType.SELL else 1)
            print(f'VALUE: {value}')
            portfolio.invested_amount = portfolio.invested_amount + value
            self.consolidate_portfolio_history(portfolio, investment)
            self.consolidate_stock(portfolio, investment)

        self.portfolio_repo.save(portfolio)

    def consolidate_stock(self, portfolio: Portfolio, investment: StockInvestment):
        stocks_dict = {s.ticker: s for s in portfolio.stocks + portfolio.reits}
        if investment.ticker in stocks_dict:
            stock_consolidated = stocks_dict[investment.ticker]
        else:
            data = self.market_data.ticker_intraday_date(investment.ticker)
            stock_consolidated = StockConsolidated(ticker=investment.ticker)
            if data.name.startswith('FII '):
                print(f'ADDING TO REITS: {investment.ticker}')
                portfolio.reits.append(stock_consolidated)
            else:
                print(f'ADDING TO STOCKS: {investment.ticker}')
                portfolio.stocks.append(stock_consolidated)
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, investment.date)
        stock_consolidated.add_investment(investment)

        self.consolidate_stock_history(stock_consolidated.history, investment)

    def consolidate_portfolio_history(self, portfolio, investment):
        history_dict = {int(h.date.timestamp()): h for h in portfolio.history}
        value = investment.amount * investment.price * (-1 if investment.operation == OperationType.SELL else 1)
        month_date = DatetimeUtils.month_first_day_datetime(investment.date)
        month_timestamp = int(month_date.timestamp())
        if month_timestamp not in history_dict:
            prev_month_timestamp = int(
                DatetimeUtils.month_first_day_datetime(investment.date - relativedelta(months=1)).timestamp())
            position = PortfolioPosition(date=month_date)
            history_dict[month_timestamp] = position
            portfolio.history.append(position)

            self._fix_portfolio_history_gap(portfolio.history, history_dict, DatetimeUtils.month_first_day_datetime(
                datetime.now()))

            if prev_month_timestamp in history_dict:
                position.total_invested = position.total_invested + history_dict[prev_month_timestamp].total_invested

        for timestamp in list(filter(lambda d: d >= month_timestamp, history_dict.keys())):
            print(f"Updating history in timestamp: {timestamp}")
            history_dict[timestamp].total_invested = history_dict[timestamp].total_invested + value

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

            self._fix_stock_history_gap(history, history_dict, investment.ticker,
                                        DatetimeUtils.month_first_day_datetime(datetime.now()))

            if prev_month_timestamp in history_dict:
                position.amount = position.amount + history_dict[prev_month_timestamp].amount

        for timestamp in list(filter(lambda d: d >= month_timestamp, history_dict.keys())):
            print(f"Updating history in timestamp: {timestamp}")
            history_dict[timestamp].amount = history_dict[timestamp].amount + amount

    def _fix_portfolio_history_gap(self, history, history_dict, date_to=None):
        timestamps = list(history_dict.keys())
        if len(timestamps) > 1:
            timestamps.sort()
            prev = datetime.fromtimestamp(timestamps[0])
            proc = prev + relativedelta(months=1)
            last = date_to or datetime.fromtimestamp(timestamps[-1])

            while proc <= last:
                print(f"PROC: {proc}")
                proc_timestamp = int(proc.timestamp())
                if proc_timestamp not in timestamps:
                    print(f'fix gap: {proc}')
                    position = PortfolioPosition(date=proc,
                                                 total_invested=history_dict[int(prev.timestamp())].total_invested)
                    history.append(position)
                    history_dict[proc_timestamp] = position
                prev = proc
                proc = proc + relativedelta(months=1)

    def _fix_stock_history_gap(self, history, history_dict, ticker, date_to=None):
        timestamps = list(history_dict.keys())
        if len(timestamps) > 1:
            timestamps.sort()
            prev = datetime.fromtimestamp(timestamps[0])
            proc = prev + relativedelta(months=1)
            last = date_to or datetime.fromtimestamp(timestamps[-1])

            monthly_data = None

            while proc <= last:
                print(f"PROC: {proc}")
                proc_timestamp = int(proc.timestamp())
                if proc_timestamp not in timestamps:
                    print(f'fix gap: {proc}')
                    if not monthly_data:
                        monthly_data = {d.date: d for d in self.market_data.ticker_monthly_data(ticker, proc)}
                    candle = monthly_data[proc.date()]
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
    start = datetime.now().timestamp()
    print(core.calculate_portfolio_performance('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    end = datetime.now().timestamp()

    print(f'DEMOROU {end - start} segundos')
    # InvestmentRepository().batch_save(
    #     investments=[StockInvestment(ticker='FLRY3', price=Decimal('23.04'), amount=Decimal(100),
    #                                  date=datetime(day=9, month=4, year=2019), costs=Decimal(0.0),
    #                                  operation=OperationType.SELL, broker='Modal',
    #                                  subject='440b0d96-395d-48bd-aaf2-58dbf7e68274', type='STOCK',
    #                                  id=str(uuid4()))])
    investmentss = InvestmentRepository().find_by_subject_mocked('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    # core.consolidate_portfolio_l('440b0d96-395d-48bd-aaf2-58dbf7e68274', investmentss)
    # for inv in investments:
    #     if inv.ticker != 'BIDI11':
    #         continue
    #     print(f"Processing inv: {inv}")
    #     try:
    #         core.consolidate_portfolio('440b0d96-395d-48bd-aaf2-58dbf7e68274', inv)
    #     except Exception as ex:
    #         print(f'{inv.ticker} EXCEPTION: {ex}')

# 1580342400
