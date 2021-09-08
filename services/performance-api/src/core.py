import logging
from datetime import datetime, timezone
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from adapters import MarketData, PortfolioRepository
from goatcommons.portfolio.models import Portfolio, StockPosition, StockConsolidated
from goatcommons.portfolio.utils import group_stock_position_per_month, create_stock_position_wrapper_list
from goatcommons.utils import DatetimeUtils
from models import StockVariation, PortfolioSummary, PortfolioPosition, \
    PortfolioHistory, StockSummary, PortfolioList, TickerConsolidatedHistory, BenchmarkPosition, \
    StockConsolidatedPosition

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PerformanceCore:
    def __init__(self, repo, market_data):
        self.repo = repo
        self.market_data = market_data

    def get_portfolio_summary(self, subject):
        portfolio = self.repo.find(subject) or Portfolio(subject=subject, ticker=subject)

        summary = PortfolioSummary()
        prev_month_adj_gross_amount = Decimal(0)
        current_month_start = DatetimeUtils.month_first_day_datetime(datetime.now())
        prev_month_start = DatetimeUtils.month_first_day_datetime(current_month_start - relativedelta(months=1))

        tickers = [s.alias_ticker or s.ticker for s in portfolio.stocks if s.latest_position.amount > 0]
        intraday_map = self.market_data.tickers_intraday_data(tickers)

        for stock in filter(lambda s: s.latest_position.amount > 0, portfolio.stocks):
            data = intraday_map[stock.alias_ticker or stock.ticker]
            summary.gross_amount += stock.latest_position.amount * data.price
            summary.day_variation += stock.latest_position.amount * (data.price - data.prev_close_price)
            summary.invested_amount += stock.latest_position.invested_value

            if stock.latest_position.date < current_month_start:
                month_data = self.market_data.ticker_month_data(stock.ticker, prev_month_start, stock.alias_ticker)
                prev_month_adj_gross_amount += stock.latest_position.amount * month_data.close
            elif stock.previous_position and stock.previous_position.amount > 0:
                month_data = self.market_data.ticker_month_data(stock.ticker, prev_month_start, stock.alias_ticker)
                prev_month_adj_gross_amount += stock.previous_position.amount * month_data.close

            if DatetimeUtils.same_year_and_month(current_month_start, stock.latest_position.date):
                summary.month_variation -= stock.latest_position.bought_value
            summary.stocks_variation.append(StockVariation(stock.alias_ticker or stock.ticker, data.change, data.price))

        summary.month_variation += summary.gross_amount - prev_month_adj_gross_amount
        return summary

    def get_portfolio_history(self, subject):
        portfolio, stock_consolidated = self.repo.find_all(subject) or (Portfolio(subject, subject), [])
        portfolio_history_map = {}

        tickers = [s.alias_ticker or s.ticker for s in portfolio.stocks]
        intraday_map = self.market_data.tickers_intraday_data(tickers)

        for stock in stock_consolidated:
            wrappers = self._fetch_stocks_history_data(stock, intraday_map)
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

    def _fetch_stocks_history_data(self, stock: StockConsolidated, intraday_map):
        grouped_positions = group_stock_position_per_month(sorted(stock.history, key=lambda h: h.date))

        monthly_map = self.market_data.ticker_monthly_data_from(stock.ticker, stock.initial_date, stock.alias_ticker)
        wrappers = create_stock_position_wrapper_list(grouped_positions)
        current = wrappers.head

        if not current:
            return []

        proc = current.data.date
        last = DatetimeUtils.month_first_day_datetime(datetime.utcnow())

        while proc <= last:
            if proc == last:
                candle = intraday_map[(stock.alias_ticker or stock.ticker)]
                current.data.close_price = candle.price
            else:
                candle = monthly_map[proc.strftime('%Y%m01')]
                current.data.close_price = candle.close

            proc += relativedelta(months=1)

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
        portfolio = self.repo.find(subject) or Portfolio(subject=subject, ticker=subject)

        stocks = []
        reits = []
        bdrs = []
        stock_gross_amount = Decimal(0)
        reit_gross_amount = Decimal(0)
        bdr_gross_amount = Decimal(0)

        tickers = [s.alias_ticker or s.ticker for s in portfolio.stocks if s.latest_position.amount > 0]
        intraday_map = self.market_data.tickers_intraday_data(tickers)

        for stock in filter(lambda s: s.latest_position.amount > 0, portfolio.stocks):
            data = intraday_map[stock.alias_ticker or stock.ticker]
            amount = stock.latest_position.amount

            summary = StockSummary(stock.ticker, stock.alias_ticker, amount, stock.latest_position.average_price,
                                   stock.latest_position.invested_value, data.price, data.price * amount)
            if data.name.startswith('FII '):
                reits.append(summary)
                reit_gross_amount = reit_gross_amount + data.price * amount
            elif int(stock.ticker[4:]) >= 30:
                bdrs.append(summary)
                bdr_gross_amount = bdr_gross_amount + data.price * amount
            else:
                stocks.append(summary)
                stock_gross_amount = stock_gross_amount + data.price * amount

        data = self.market_data.ibov_from_date(portfolio.initial_date)
        ibov_history = [BenchmarkPosition(candle.candle_date, candle.open_price, candle.close_price) for candle in data]

        return PortfolioList(stock_gross_amount, reit_gross_amount, bdr_gross_amount, stocks, reits, bdrs, ibov_history)

    def get_ticker_consolidated_history(self, subject, ticker):
        stocks_consolidated = self.repo.find_alias_ticker(subject, ticker)
        if not stocks_consolidated:
            return

        intraday_map = self.market_data.tickers_intraday_data([ticker])
        consolidated_map = {}
        for stock_consolidated in stocks_consolidated:
            wrappers = self._fetch_stocks_history_data(stock_consolidated, intraday_map)
            if not wrappers:
                continue
            current = wrappers.head

            while current:
                key = current.data.date.strftime('%Y%m%d')
                if key not in consolidated_map:
                    consolidated_map[key] = StockConsolidatedPosition(current.data.date, current.gross_value,
                                                                      current.current_invested_value,
                                                                      current.month_variation_percent)
                else:
                    consolidated = consolidated_map[key]
                    prev_gross_value = (consolidated.gross_value * 100) / (100 + consolidated.variation_perc) + (
                            current.gross_value * 100) / (100 + current.month_variation_percent)
                    variation = (((
                                          consolidated.gross_value + current.gross_value) * 100 / prev_gross_value) - 100).quantize(
                        Decimal('0.01'))
                    consolidated.gross_value += current.gross_value
                    consolidated.invested_value += current.current_invested_value
                    consolidated.variation_perc = variation

                current = current.next

        return TickerConsolidatedHistory(consolidated_map.values())


def main():
    subject = '41e4a793-3ef5-4413-82e2-80919bce7c1a'
    core = PerformanceCore(repo=PortfolioRepository(), market_data=MarketData())
    # response = core.get_portfolio_summary(subject)
    # response = core.get_portfolio_history(subject)
    # response = core.get_portfolio_list(subject)
    response = core.get_ticker_consolidated_history(subject, 'AESB3')
    print(response)


if __name__ == '__main__':
    main()
