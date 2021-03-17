from datetime import datetime
from decimal import Decimal
from itertools import groupby
from typing import List

from dateutil.relativedelta import relativedelta

from adapters import InvestmentRepository, MarketData, PortfolioRepository
from goatcommons.constants import OperationType, InvestmentsType
from goatcommons.models import StockInvestment
from goatcommons.utils import DatetimeUtils
from models import Portfolio, StockConsolidated, StockPosition, PortfolioPosition


class PerformanceCore:
    def __init__(self):
        self.investment_repo = InvestmentRepository()
        self.portfolio_repo = PortfolioRepository()
        self.market_data = MarketData()

    def consolidate_port_new_and_old_change_name(self, subject, new_investments, old_investments):
        """
            new_investments is a new or a newer version of the investment
            old_investments is an old a investment before edit or deletion

            new investments will be added to the portfolio and old investments will be subtracted from the portfolio
        """
        return
        # new_invest_map = groupby(sorted(new_investments, key=lambda i: i.ticker), key=lambda i: i.ticker)
        # # old_invest_map = groupby(sorted(old_investments, key=lambda i: i.ticker), key=lambda i: i.ticker)
        #
        # portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)
        # for ticker, investments in new_invest_map:
        #     stock_consolidated = next((stock for stock in portfolio.stocks if stock.ticker == ticker), {})
        #     if not stock_consolidated:
        #         stock_consolidated = StockConsolidated(ticker=ticker)
        #         portfolio.stocks = stock_consolidated
        #
        #     investments = sorted(list(investments), key=lambda i: i.date)
        #     for i in investments:
        #         self.consolidate_stock_new(stock_consolidated, i)
        #     self._fix_stock_history_gap(stock_consolidated.history, ticker)
        #
        # all_stocks_history = [item for sublist in [s.history for s in portfolio.stocks] for item in sublist]
        # portfolio_history_map = {}
        # portfolio.invested_amount = Decimal(0)
        #
        # for stock_position in all_stocks_history:
        #     if stock_position.date not in portfolio_history_map:
        #         p_position = PortfolioPosition(stock_position.date)
        #         portfolio_history_map[stock_position.date] = p_position
        #     else:
        #         p_position = portfolio_history_map[stock_position.date]
        #
        #     portfolio.invested_amount = portfolio.invested_amount + stock_position.invested_amount
        #
        #     p_position.total_invested = p_position.total_invested + stock_position.invested_amount
        #     if stock_position.amount > 0:
        #         p_position.gross_amount = p_position.gross_amount + stock_position.amount * stock_position.close_price
        # portfolio.history = list(portfolio_history_map.values())
        #
        # self.portfolio_repo.save(portfolio)

    def consolidate_stock_new(self, stock_consolidated: StockConsolidated, inv: StockInvestment):
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, inv.date)
        stock_consolidated.add_investment(inv)

        month_date = DatetimeUtils.month_first_day_datetime(inv.date)
        candle = self.market_data.ticker_month_data(inv.ticker, inv.date)

        h_position = next((position for position in stock_consolidated.history if position.date == month_date), {})
        if not h_position:
            prev_positions = sorted([position for position in stock_consolidated.history if position.date < month_date],
                                    key=lambda p: p.date)
            amount = prev_positions[-1].amount if prev_positions else Decimal(0)

            h_position = StockPosition(month_date, candle.open, candle.close, amount, invested_amount=Decimal(0))
            stock_consolidated.history.append(h_position)

        inv_amount = (inv.amount if inv.operation == OperationType.BUY else - inv.amount)
        h_position.amount = h_position.amount + inv_amount
        h_position.invested_amount = h_position.invested_amount + inv_amount

        for position in [position for position in stock_consolidated.history if position.date > month_date]:
            position.amount = position.amount + inv_amount

    def _fix_stock_history_gap(self, history, ticker):
        history_dict = {int(h.date.timestamp()): h for h in history}
        timestamps = list(history_dict.keys())
        timestamps.sort()

        prev = datetime.fromtimestamp(timestamps[0])
        proc = prev + relativedelta(months=1)
        last = DatetimeUtils.month_first_day_datetime(datetime.now())

        while proc <= last:
            proc_timestamp = int(proc.timestamp())
            if proc_timestamp not in timestamps:
                print(f'fix gap: {proc}')
                candle = self.market_data.ticker_month_data(ticker, proc.date())
                position = StockPosition(date=proc, open_price=candle.open, close_price=candle.close,
                                         amount=history_dict[int(prev.timestamp())].amount)
                history.append(position)
                history_dict[proc_timestamp] = position
            prev = proc
            proc = proc + relativedelta(months=1)

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
            portfolio.initial_date = min(investment.date, portfolio.initial_date)

            if investment.type == InvestmentsType.STOCK:
                value = investment.amount * investment.price * (
                    -1 if investment.operation == OperationType.SELL else 1)
                print(f'VALUE: {value}')
                portfolio.invested_amount = portfolio.invested_amount + value
                self.consolidate_portfolio_history(portfolio, investment)
                self.consolidate_stock(portfolio, investment)

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
