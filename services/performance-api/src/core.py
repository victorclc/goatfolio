import logging
from datetime import datetime, timezone
from decimal import Decimal
from itertools import groupby
from typing import List

from dateutil.relativedelta import relativedelta

from adapters import MarketData, PortfolioRepository
from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment
from goatcommons.utils import DatetimeUtils
from models import Portfolio, StockConsolidated, StockPosition, PortfolioPosition, StockVariation, PortfolioSummary, \
    PortfolioHistory, StockSummary, PortfolioList, TickerConsolidatedHistory

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SafePerformanceCore:
    def __init__(self):
        self.portfolio_repo = PortfolioRepository()
        self.market_data = MarketData()

    def consolidate_portfolio(self, subject, new_investments, old_investments):
        for inv in old_investments:
            inv.amount = -1 * inv.amount
        investments_map = groupby(sorted(new_investments + old_investments, key=lambda i: i.ticker),
                                  key=lambda i: i.ticker)

        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)
        for ticker, investments in investments_map:
            stock_consolidated = next((stock for stock in portfolio.stocks if stock.ticker == ticker), {})
            if not stock_consolidated:
                stock_consolidated = StockConsolidated(ticker=ticker)
                portfolio.stocks.append(stock_consolidated)

            investments = sorted(list(investments), key=lambda i: i.date)
            for inv in investments:
                if inv.amount > 0:
                    portfolio.initial_date = min(portfolio.initial_date, inv.date)
                self._consolidate_stock(stock_consolidated, inv)

        self.portfolio_repo.save(portfolio)

    def get_portfolio_summary(self, subject):
        # used on summary page
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)

        return PortfolioSummary(*self._calculate_stocks_performance(portfolio.stocks))

    def get_portfolio_history(self, subject):
        # used to build rentability charts
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)

        self._fetch_stocks_history_data(portfolio.stocks)

        all_stocks_history = [item for sublist in [s.history for s in portfolio.stocks] for item in sublist]
        portfolio_history_map = {}

        for stock_position in sorted(all_stocks_history, key=lambda h: h.date):
            if stock_position.date not in portfolio_history_map:
                p_position = PortfolioPosition(stock_position.date)
                portfolio_history_map[stock_position.date] = p_position
            else:
                p_position = portfolio_history_map[stock_position.date]

            p_position.total_invested = p_position.total_invested + stock_position.invested_value - stock_position.sold_value
            if stock_position.amount > 0:
                p_position.gross_amount = p_position.gross_amount + stock_position.amount * stock_position.close_price

        data = self.market_data.ibov_from_date(portfolio.initial_date)
        ibov_history = [
            StockPosition(date=datetime(candle.date.year, candle.date.month, candle.date.day, tzinfo=timezone.utc),
                          open_price=candle.open, close_price=candle.close) for candle in data]
        return PortfolioHistory(history=list(portfolio_history_map.values()), ibov_history=ibov_history)

    def get_portfolio_list(self, subject):
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)

        stocks = []
        reits = []
        bdrs = []
        stock_gross_amount = Decimal(0)
        reit_gross_amount = Decimal(0)
        bdr_gross_amount = Decimal(0)

        for stock in portfolio.stocks:
            if stock.current_amount <= 0:
                continue

            data = self.market_data.ticker_intraday_date(stock.alias_ticker or stock.ticker)

            if data.name.startswith('FII '):
                reits.append(
                    StockSummary(stock.ticker, stock.alias_ticker, stock.current_amount, stock.average_price,
                                 stock.current_invested,
                                 data.price, data.price * stock.current_amount))
                reit_gross_amount = reit_gross_amount + data.price * stock.current_amount
            elif int(stock.ticker[4:]) >= 30:
                bdrs.append(
                    StockSummary(stock.ticker, stock.alias_ticker, stock.current_amount, stock.average_price,
                                 stock.current_invested,
                                 data.price, data.price * stock.current_amount))
                bdr_gross_amount = bdr_gross_amount + data.price * stock.current_amount
            else:
                stocks.append(
                    StockSummary(stock.ticker, stock.alias_ticker, stock.current_amount, stock.average_price,
                                 stock.current_invested,
                                 data.price, data.price * stock.current_amount))
                stock_gross_amount = stock_gross_amount + data.price * stock.current_amount

        data = self.market_data.ibov_from_date(portfolio.initial_date)
        ibov_history = [
            StockPosition(date=candle.candle_date, open_price=candle.open_price, close_price=candle.close_price) for
            candle in data]

        return PortfolioList(stock_gross_amount, reit_gross_amount, bdr_gross_amount, stocks, reits, bdrs, ibov_history)

    def get_ticker_consolidated_history(self, subject, ticker):
        portfolio = self.portfolio_repo.find(subject) or Portfolio(subject=subject)
        stock_consolidated = next((stock for stock in portfolio.stocks if stock.ticker == ticker), {})

        self._fetch_stocks_history_data([stock_consolidated])

        return TickerConsolidatedHistory(stock_consolidated.history)

    def _fetch_stocks_history_data(self, stocks: List[StockConsolidated]):

        for stock in stocks:
            history_dict = {int(h.date.timestamp()): h for h in stock.history}
            timestamps = list(history_dict.keys())
            timestamps.sort()

            monthly_map = self.market_data.ticker_monthly_data_from(stock.ticker, stock.initial_date,
                                                                    stock.alias_ticker)

            logger.info(f'Monthly Map: {monthly_map}')
            prev = datetime.fromtimestamp(timestamps[0], tz=timezone.utc)
            proc = prev
            last = DatetimeUtils.month_first_day_datetime(datetime.utcnow())

            while proc <= last:
                proc_timestamp = int(proc.timestamp())
                if proc_timestamp not in timestamps:
                    position = StockPosition(date=proc, amount=history_dict[int(prev.timestamp())].amount)
                    stock.history.append(position)
                    history_dict[proc_timestamp] = position

                if proc == last:
                    candle = self.market_data.ticker_intraday_date(stock.alias_ticker or stock.ticker)
                    price = candle.price
                    _open = None
                else:
                    candle = monthly_map[proc.strftime('%Y%m01')]
                    if not candle:
                        logger.info(f'CANDLE MISSING: {stock.ticker} {proc}')
                    price = candle.close if candle else Decimal(0)
                    _open = candle.open if candle else Decimal(0)

                history_dict[proc_timestamp].close_price = price
                history_dict[proc_timestamp].open_price = _open

                prev = proc
                proc = proc + relativedelta(months=1)

    def _calculate_stocks_performance(self, stocks: List[StockConsolidated]):
        invested_amount = Decimal(0)
        gross_amount = Decimal(0)
        prev_day_gross_amount = Decimal(0)
        prev_month_gross_amount = Decimal(0)
        month_variation = Decimal(0)
        stock_variation = []

        now = datetime.now()
        prev_month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc) - relativedelta(months=1)
        for stock in stocks:
            if stock.current_amount <= 0:
                continue
            invested_amount = invested_amount + sum(s.invested_value - s.sold_value for s in stock.history)

            data = self.market_data.ticker_intraday_date(stock.alias_ticker or stock.ticker)
            gross_amount = gross_amount + stock.current_amount * data.price
            prev_day_gross_amount = prev_day_gross_amount + stock.current_amount * data.prev_close_price

            prev_month_amount = stock.prev_month_amount
            if prev_month_amount > 0:
                month_data = self.market_data.ticker_month_data(stock.ticker, prev_month_start, stock.alias_ticker)
                if stock.sold_amount_current_month > 0:
                    prev_month_amount = prev_month_amount - stock.sold_amount_current_month
                prev_month_gross_amount = prev_month_gross_amount + month_data.close * prev_month_amount
            month_variation = month_variation - stock.value_invested_current_month

            stock_variation.append(StockVariation(stock.alias_ticker or stock.ticker, data.change, data.price))

        day_variation = gross_amount - prev_day_gross_amount
        month_variation = month_variation + gross_amount - prev_month_gross_amount
        return invested_amount, gross_amount, day_variation, month_variation, stock_variation

    @staticmethod
    def _consolidate_stock(stock_consolidated: StockConsolidated, inv: StockInvestment):
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, inv.date)
        stock_consolidated.add_investment(inv)
        if inv.alias_ticker:
            stock_consolidated.alias_ticker = inv.alias_ticker

        month_date = DatetimeUtils.month_first_day_datetime(inv.date)
        h_position = next((position for position in stock_consolidated.history if position.date == month_date), {})
        if not h_position:
            prev_positions = sorted([position for position in stock_consolidated.history if position.date < month_date],
                                    key=lambda p: p.date)
            amount = prev_positions[-1].amount if prev_positions else Decimal(0)

            h_position = StockPosition(date=month_date, amount=amount, invested_value=Decimal(0))
            stock_consolidated.history.append(h_position)

        if inv.operation == OperationType.BUY:
            h_position.bought_amount = h_position.bought_amount + inv.amount
            h_position.amount = h_position.amount + inv.amount
            h_position.invested_value = h_position.invested_value + inv.amount * inv.price
        elif inv.operation == OperationType.SELL:
            h_position.sold_amount = h_position.sold_amount + inv.amount
            h_position.sold_value = h_position.sold_value + inv.amount * stock_consolidated.average_price
            h_position.realized_profit = h_position.realized_profit + inv.amount * inv.price - h_position.sold_value
            h_position.amount = h_position.amount - inv.amount
        elif inv.operation in [OperationType.SPLIT, OperationType.INCORP_ADD]:
            # TODO POSSIBLE BUG HERE, when calculating previous month variation
            h_position.amount = h_position.amount + inv.amount
        elif inv.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            # TODO POSSIBLE BUG HERE, when calculating previous month variation
            h_position.amount = h_position.amount - inv.amount

        inv_amount = (inv.amount if inv.operation in [OperationType.BUY, OperationType.SPLIT,
                                                      OperationType.INCORP_ADD] else - inv.amount)
        for position in [position for position in stock_consolidated.history if position.date > month_date]:
            position.amount = position.amount + inv_amount


if __name__ == '__main__':
    # investmentss = InvestmentRepository().find_by_subject('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    # investmentss = list(filter(lambda i: i.id == 'ea5a8baa-0fd7-429f-aac1-ef28c4e039d3', investmentss))
    # print(SafePerformanceCore().consolidate_portfolio('440b0d96-395d-48bd-aaf2-58dbf7e68274', investmentss, []))
    # print(SafePerformanceCore().get_portfolio_summary('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    # print(SafePerformanceCore().get_portfolio_history('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    # print(SafePerformanceCore().get_portfolio_list('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    print(SafePerformanceCore().get_ticker_consolidated_history('440b0d96-395d-48bd-aaf2-58dbf7e68274', 'BBAS3'))
