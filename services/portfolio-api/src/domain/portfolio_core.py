import logging
from itertools import groupby

from domain.models.investment import StockInvestment
from domain.ports.out.portfolio_repository import PortfolioRepository
from domain.enums.operation_type import OperationType

from domain.models.portfolio import (
    Portfolio,
    StockPositionMonthlySummary,
    StockSummary,
    StockConsolidated,
    StockPosition,
)

from domain.utils.stock_position_wrapper import (
    create_stock_position_wrapper_list,
    group_stock_position_per_month,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(funcName)s %(levelname)-s: %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PortfolioCore:
    def __init__(self, repo: PortfolioRepository):
        self.repo = repo

    def consolidate_portfolio(self, subject, new_investments, old_investments):
        self._invert_investments_list(old_investments)
        portfolio = self.repo.find(subject)

        for current_ticker, investments in self._group_by_current_ticker_name(
            new_investments + old_investments
        ):
            consolidated_list = self.repo.find_alias_ticker(subject, current_ticker)

            for ticker, t_investments in groupby(
                sorted(list(investments), key=lambda i: i.ticker),
                key=lambda i: i.ticker,
            ):
                consolidated = self._find_ticker_consolidated(
                    ticker, subject, consolidated_list
                )

                for inv in sorted(list(t_investments), key=lambda i: i.date):
                    if inv.operation in [
                        OperationType.INCORP_ADD,
                        OperationType.INCORP_SUB,
                    ]:
                        self._remove_ticker_from_portfolio_summary(ticker, portfolio)
                    if inv.amount > 0:
                        portfolio.initial_date = min(portfolio.initial_date, inv.date)
                    self._consolidate_stock(consolidated, inv)
                self.repo.save_stock_consolidated(consolidated)
            self._consolidate_portfolio_stock(
                current_ticker,
                portfolio,
                sum(consolidated_list[1:], consolidated_list[0]),
            )
        self.repo.save_portfolio(portfolio)

    @staticmethod
    def _remove_ticker_from_portfolio_summary(ticker, portfolio):
        results = list(filter(lambda s: s.ticker == ticker, portfolio.stocks))
        if results:
            logger.info(f"Removing {ticker} from portfoio summary.")
            portfolio.stocks.remove(results[0])

    def _find_ticker_consolidated(self, ticker, subject, consolidated_list):
        consolidated = next(
            (
                stock
                for stock in consolidated_list
                if stock.ticker == ticker or stock.alias_ticker == ticker
            ),
            None,
        )
        if not consolidated:
            response = self.repo.find_ticker(subject, ticker)
            if response:
                consolidated = response[0]
            else:
                consolidated = StockConsolidated(subject=subject, ticker=ticker)
            consolidated_list.append(consolidated)

        return consolidated

    @staticmethod
    def _group_by_current_ticker_name(investments):
        by_ticker = groupby(
            sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker
        )
        for ticker, t_investments in by_ticker:
            t_investments = list(t_investments)
            alias_ticker = next(
                (i.alias_ticker for i in t_investments if i.alias_ticker), None
            )
            if alias_ticker:
                for i in t_investments:
                    i.alias_ticker = alias_ticker
        return groupby(
            sorted(investments, key=lambda i: i.current_ticker_name),
            key=lambda i: i.current_ticker_name,
        )

    @staticmethod
    def _invert_investments_list(investments):
        for i in investments:
            i.amount *= -1
        return investments

    @staticmethod
    def _consolidate_portfolio_stock(
        ticker: str, portfolio: Portfolio, stock_consolidated: StockConsolidated
    ):
        monthly_positions = group_stock_position_per_month(
            sorted(stock_consolidated.history, key=lambda h: h.date)
        )
        wrapper = create_stock_position_wrapper_list(monthly_positions)
        if wrapper.tail is None:
            return
        current = wrapper.tail
        previous = current.prev

        latest_position = StockPositionMonthlySummary(
            date=current.data.date,
            amount=current.amount,
            invested_value=current.current_invested_value,
            bought_value=current.data.bought_value,
            average_price=current.average_price,
        )
        previous_position = None
        if previous:
            previous_position = StockPositionMonthlySummary(
                date=previous.data.date, amount=previous.amount
            )

        stock_summary = next(
            (
                stock
                for stock in portfolio.stocks
                if stock.ticker == ticker or stock.alias_ticker == ticker
            ),
            None,
        )
        if stock_summary:
            stock_summary.ticker = stock_consolidated.ticker
            stock_summary.alias_ticker = stock_consolidated.alias_ticker
            stock_summary.latest_position = latest_position
            stock_summary.previous_position = previous_position
        else:
            stock_summary = StockSummary(
                stock_consolidated.ticker,
                alias_ticker=stock_consolidated.alias_ticker,
                latest_position=latest_position,
                previous_position=previous_position,
            )
            portfolio.stocks.append(stock_summary)

    @staticmethod
    def _consolidate_stock(stock_consolidated: StockConsolidated, inv: StockInvestment):
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, inv.date)
        if inv.alias_ticker:
            stock_consolidated.alias_ticker = inv.alias_ticker

        h_position = next(
            (
                position
                for position in stock_consolidated.history
                if position.date == inv.date
            ),
            None,
        )
        if not h_position:
            h_position = StockPosition.from_stock_investment(inv)
            stock_consolidated.history.append(h_position)
        else:
            h_position.add_investment(inv)

        if h_position.is_empty():
            stock_consolidated.history.remove(h_position)
