import logging
from datetime import datetime, timezone
from decimal import Decimal
from itertools import groupby

from dateutil.relativedelta import relativedelta

from adapters import PortfolioRepository, MarketData
from goatcommons.models import StockInvestment
from goatcommons.utils import DatetimeUtils
from models import Portfolio, StockConsolidated, StockPosition, StockVariation, PortfolioSummary, PortfolioPosition, \
    PortfolioHistory, StockSummary, PortfolioList, TickerConsolidatedHistory, BenchmarkPosition, \
    StockConsolidatedPosition
from wrappers import PositionDoublyLinkedList

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PerformanceCore:
    def __init__(self):
        self.repo = PortfolioRepository()
        self.market_data = MarketData()

    def consolidate_portfolio(self, subject, new_investments, old_investments):
        for inv in old_investments:
            inv.amount = -1 * inv.amount
        investments_map = groupby(sorted(new_investments + old_investments, key=lambda i: i.ticker),
                                  key=lambda i: i.ticker)

        portfolio = self.repo.find(subject) or Portfolio(subject=subject)
        for ticker, investments in investments_map:
            stock_consolidated = next(
                (stock for stock in portfolio.stocks if stock.ticker == ticker or stock.alias_ticker == ticker), {})
            if not stock_consolidated:
                stock_consolidated = StockConsolidated(ticker=ticker)
                portfolio.stocks.append(stock_consolidated)

            investments = sorted(list(investments), key=lambda i: i.date)
            for inv in investments:
                if inv.amount > 0:
                    portfolio.initial_date = min(portfolio.initial_date, inv.date)
                self._consolidate_stock(stock_consolidated, inv)

        self.repo.save(portfolio)

        return portfolio

    @staticmethod
    def _consolidate_stock(stock_consolidated: StockConsolidated, inv: StockInvestment):
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, inv.date)
        if inv.alias_ticker:
            stock_consolidated.alias_ticker = inv.alias_ticker

        h_position = next((position for position in stock_consolidated.history if position.date == inv.date), {})
        if not h_position:
            h_position = StockPosition.from_stock_investment(inv)
            stock_consolidated.history.append(h_position)
        else:
            h_position.add_investment(inv)

        if h_position.is_empty():
            stock_consolidated.history.remove(h_position)

    def get_portfolio_summary(self, subject):
        portfolio = self.repo.find(subject) or Portfolio(subject=subject)

        gross_amount = Decimal(0)
        invested_amount = Decimal(0)
        day_variation = Decimal(0)
        prev_month_adj_gross_amount = Decimal(0)
        month_variation = Decimal(0)
        stock_variation = []

        prev_month_start = datetime.now(tz=timezone.utc).replace(day=1) - relativedelta(months=1)
        current_month_start = datetime.now(tz=timezone.utc).replace(day=1)
        for stock in portfolio.stocks:
            sorted_history = sorted(stock.history, key=lambda h: h.date)
            grouped_positions = self._group_stock_position_per_month(sorted_history)
            wrappers = self._create_stock_position_wrapper_list(grouped_positions)
            current = wrappers.tail

            if not current or current.amount <= 0:
                continue
            if current_month_start.date() != current.data.date.date():
                wrappers.append(StockPosition(current_month_start))
                current = wrappers.tail

            data = self.market_data.ticker_intraday_date(stock.alias_ticker or stock.ticker)
            gross_amount += current.amount * data.price
            day_variation += current.amount * (data.price - data.prev_close_price)
            invested_amount += current.current_invested_value

            previous = current.prev
            if previous and previous.amount > 0:
                month_data = self.market_data.ticker_month_data(stock.ticker, prev_month_start, stock.alias_ticker)
                previous.data.close_price = month_data.close
                prev_month_adj_gross_amount += current.prev_adjusted_gross_value
            print(f'TICKER: {stock.ticker}')
            print(prev_month_adj_gross_amount)

            month_variation -= current.data.bought_value
            stock_variation.append(StockVariation(stock.alias_ticker or stock.ticker, data.change, data.price))

        month_variation = month_variation + gross_amount - prev_month_adj_gross_amount
        return PortfolioSummary(invested_amount, gross_amount, day_variation, month_variation, stock_variation)

    @staticmethod
    def _group_stock_position_per_month(stock_positions):
        grouped_positions = []
        for date, positions in groupby(stock_positions, key=lambda p: p.date.replace(day=1)):
            grouped = StockPosition(date)
            for position in positions:
                grouped = grouped + position
            grouped_positions.append(grouped)
        return grouped_positions

    @staticmethod
    def _create_stock_position_wrapper_list(positions):
        doubly = PositionDoublyLinkedList()
        for h in positions:
            doubly.append(h)
        return doubly

    def get_portfolio_history(self, subject):
        portfolio = self.repo.find(subject) or Portfolio(subject=subject)

        portfolio_history_map = {}
        for stock in portfolio.stocks:
            wrappers = self._fetch_stocks_history_data(stock)
            if not wrappers:
                continue
            current = wrappers.head

            while current:
                if current.data.date not in portfolio_history_map:
                    p_position = PortfolioPosition(current.data.date)
                    portfolio_history_map[current.data.date] = p_position
                else:
                    p_position = portfolio_history_map[current.data.date]

                p_position.invested_value = p_position.invested_value + current.node_invested_value
                if current.amount > 0:
                    p_position.gross_value = p_position.gross_value + current.gross_value
                current = current.next

        data = self.market_data.ibov_from_date(portfolio.initial_date)
        ibov_history = [BenchmarkPosition(candle.candle_date, candle.open_price, candle.close_price) for candle in data]
        return PortfolioHistory(history=list(portfolio_history_map.values()), ibov_history=ibov_history)

    def _fetch_stocks_history_data(self, stock: StockConsolidated):
        grouped_positions = self._group_stock_position_per_month(sorted(stock.history, key=lambda h: h.date))

        monthly_map = self.market_data.ticker_monthly_data_from(stock.ticker, stock.initial_date, stock.alias_ticker)
        wrappers = self._create_stock_position_wrapper_list(grouped_positions)
        current = wrappers.head

        if not current:
            return []

        proc = current.data.date
        last = DatetimeUtils.month_first_day_datetime(datetime.utcnow())

        while proc <= last:
            if proc == last:
                candle = self.market_data.ticker_intraday_date(stock.alias_ticker or stock.ticker)
                price = candle.price
            else:
                candle = monthly_map[proc.strftime('%Y%m01')]
                if not candle:
                    logger.info(f'CANDLE MISSING: {stock.ticker} {proc}')
                price = candle.close if candle else Decimal(0)

            current.data.close_price = price
            proc = proc + relativedelta(months=1)

            if current.next:
                if current.next.data.date != proc:
                    new = StockPosition(proc)
                    grouped_positions.append(new)
                    wrappers.insert(current, new)
                current = current.next
            elif proc <= last:
                new = StockPosition(proc)
                grouped_positions.append(new)
                wrappers.insert(current, new)
                current = current.next

        return wrappers

    def get_portfolio_list(self, subject):
        portfolio = self.repo.find(subject) or Portfolio(subject=subject)

        stocks = []
        reits = []
        bdrs = []
        stock_gross_amount = Decimal(0)
        reit_gross_amount = Decimal(0)
        bdr_gross_amount = Decimal(0)

        for stock in portfolio.stocks:
            current = self._create_stock_position_wrapper_list(stock.history).tail
            if not current:
                continue
            amount = current.amount
            if amount <= 0:
                continue

            data = self.market_data.ticker_intraday_date(stock.alias_ticker or stock.ticker)

            if data.name.startswith('FII '):
                reits.append(
                    StockSummary(stock.ticker, stock.alias_ticker, amount, current.average_price,
                                 current.current_invested_value,
                                 data.price, data.price * amount))
                reit_gross_amount = reit_gross_amount + data.price * amount
            elif int(stock.ticker[4:]) >= 30:
                bdrs.append(
                    StockSummary(stock.ticker, stock.alias_ticker, amount, current.average_price,
                                 current.current_invested_value,
                                 data.price, data.price * amount))
                bdr_gross_amount = bdr_gross_amount + data.price * amount
            else:
                stocks.append(
                    StockSummary(stock.ticker, stock.alias_ticker, amount, current.average_price,
                                 current.current_invested_value,
                                 data.price, data.price * amount))
                stock_gross_amount = stock_gross_amount + data.price * amount

        data = self.market_data.ibov_from_date(portfolio.initial_date)
        ibov_history = [BenchmarkPosition(candle.candle_date, candle.open_price, candle.close_price) for candle in data]

        return PortfolioList(stock_gross_amount, reit_gross_amount, bdr_gross_amount, stocks, reits, bdrs, ibov_history)

    def get_ticker_consolidated_history(self, subject, ticker):
        portfolio = self.repo.find(subject) or Portfolio(subject=subject)
        stock_consolidated = next((stock for stock in portfolio.stocks if stock.ticker == ticker), {})

        wrappers = self._fetch_stocks_history_data(stock_consolidated)
        current = wrappers.head
        consolidated = []
        while current:
            consolidated.append(
                StockConsolidatedPosition(current.data.date, current.gross_value, current.current_invested_value,
                                          current.month_variation_percent))
            current = current.next

        return TickerConsolidatedHistory(consolidated)


if __name__ == '__main__':
    # investmentss = InvestmentRepository().find_by_subject('440b0d96-395d-48bd-aaf2-58dbf7e68274')
    # investmentss = list(filter(lambda i: i.id == 'ea5a8baa-0fd7-429f-aac1-ef28c4e039d3', investmentss))
    #     print(PerformanceCore().consolidate_portfolio('440b0d96-395d-48bd-aaf2-58dbf7e68274', investmentss, []))
    print(PerformanceCore().get_portfolio_summary('41e4a793-3ef5-4413-82e2-80919bce7c1a'))
    # print(PerformanceCore().get_portfolio_history('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    # print(PerformanceCore().get_portfolio_list('440b0d96-395d-48bd-aaf2-58dbf7e68274'))
    # print(PerformanceCore().get_ticker_consolidated_history('440b0d96-395d-48bd-aaf2-58dbf7e68274', 'BIDI11'))
