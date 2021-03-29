from datetime import datetime
from decimal import Decimal
from itertools import groupby
from typing import List

from dateutil.relativedelta import relativedelta

from adapters import InvestmentRepository, MarketData, PortfolioRepository
from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment
from goatcommons.utils import DatetimeUtils
from models import Portfolio, StockConsolidated, StockPosition, PortfolioPosition


class PerformanceCore:
    def __init__(self):
        self.investment_repo = InvestmentRepository()
        self.portfolio_repo = PortfolioRepository()
        self.market_data = MarketData()

    def consolidate_portfolio(self, subject, new_investments, old_investments):
        """
            new_investments is a new or a newer version of the investment
            old_investments is an old a investment before edit or deletion

            new investments will be added to the portfolio and old investments will be subtracted from the portfolio
        """
        for inv in old_investments:
            inv.amount = -1 * inv.amount
        investments_map = groupby(sorted(new_investments + old_investments, key=lambda i: i.ticker),
                                  key=lambda i: i.ticker)

        portfolio = Portfolio(subject=subject)

        for ticker, investments in investments_map:
            stock_consolidated = next((stock for stock in portfolio.stocks if stock.ticker == ticker), {})
            if not stock_consolidated:
                stock_consolidated = StockConsolidated(ticker=ticker)
                portfolio.stocks.append(stock_consolidated)

            investments = sorted(list(investments), key=lambda i: i.date)
            for inv in investments:
                if inv.amount > 0:
                    portfolio.initial_date = min(portfolio.initial_date, inv.date)
                self.consolidate_stock(stock_consolidated, inv)
            self._fix_stock_history_gap(stock_consolidated.history, ticker)

        self.consolidate_portfolio_summary(portfolio)
        self.portfolio_repo.save(portfolio)

    @staticmethod
    def consolidate_portfolio_summary(portfolio: Portfolio):
        all_stocks_history = [item for sublist in [s.history for s in portfolio.stocks] for item in sublist]
        portfolio_history_map = {}
        portfolio.invested_amount = Decimal(0)

        for stock_position in all_stocks_history:
            if stock_position.date not in portfolio_history_map:
                p_position = PortfolioPosition(stock_position.date)
                portfolio_history_map[stock_position.date] = p_position
            else:
                p_position = portfolio_history_map[stock_position.date]

            portfolio.invested_amount = portfolio.invested_amount + stock_position.invested_amount

            p_position.total_invested = p_position.total_invested + stock_position.invested_amount
            if stock_position.amount > 0:
                p_position.gross_amount = p_position.gross_amount + stock_position.amount * stock_position.close_price
        portfolio.history = list(portfolio_history_map.values())

    def consolidate_stock(self, stock_consolidated: StockConsolidated, inv: StockInvestment):
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

        if inv.operation == OperationType.BUY:
            h_position.amount = h_position.amount + inv.amount
            h_position.invested_amount = h_position.invested_amount + inv.amount * inv.price
        else:
            h_position.invested_amount = h_position.invested_amount - inv.amount * stock_consolidated.average_price
            h_position.amount = h_position.amount - inv.amount

        inv_amount = (inv.amount if inv.operation == OperationType.BUY else - inv.amount)
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

    def calculate_today_performance(self, subject):
        assert subject
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)

        stocks = []
        reits = []
        for stock in portfolio.stocks:
            data = self.market_data.ticker_intraday_date(stock.ticker)
            if data.name.startswith('FII '):
                reits.append(stock)
            else:
                stocks.append(stock)
        stock_performance = self._calculate_stocks_performance(stocks)
        reit_performance = self._calculate_stocks_performance(reits)

        portfolio.stocks = stocks
        portfolio.reits = reits
        self.consolidate_portfolio_summary(portfolio)

        portfolio.stocks, portfolio.stock_gross_amount, portfolio.stock_prev_gross_amount = stock_performance
        portfolio.reits, portfolio.reit_gross_amount, portfolio.reit_prev_gross_amount = reit_performance

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
                self._fix_stock_history_gap(stock.history, stock.ticker)
                sorted(stock.history, key=lambda h: h.date)[-1].close_price = data.price
            else:
                print(f"REMOVING {stock.ticker}")
                zeroed_stocks.append(stock)
        return [stock for stock in stocks if stock not in zeroed_stocks], gross_amount, prev_gross_amount


if __name__ == '__main__':
    investments = InvestmentRepository().find_by_subject('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    PerformanceCore().consolidate_portfolio('440b0d96-395d-48bd-aaf2-58dbf7e68274', investments, [])
