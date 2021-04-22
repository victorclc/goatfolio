from decimal import Decimal
from itertools import groupby

from adapters import PortfolioRepository, MarketData
from goatcommons.models import StockInvestment
from models import Portfolio, StockConsolidated, StockPosition


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
            stock_consolidated = next((stock for stock in portfolio.stocks if stock.ticker == ticker), {})
            if not stock_consolidated:
                stock_consolidated = StockConsolidated(ticker=ticker)
                portfolio.stocks.append(stock_consolidated)

            investments = sorted(list(investments), key=lambda i: i.date)
            for inv in investments:
                if inv.amount > 0:
                    portfolio.initial_date = min(portfolio.initial_date, inv.date)
                self._consolidate_stock(stock_consolidated, inv)

    @staticmethod
    def _consolidate_stock(stock_consolidated: StockConsolidated, inv: StockInvestment):
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, inv.date)
        stock_consolidated.add_investment(inv)

        if inv.alias_ticker:
            stock_consolidated.alias_ticker = inv.alias_ticker

        h_position = next((position for position in stock_consolidated.history if position.date == inv.date), {})

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
