import logging
from datetime import datetime, timezone
from decimal import Decimal
from itertools import groupby
from uuid import uuid4

from adapters import InvestmentRepository, PortfolioRepository
from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment
from goatcommons.portfolio.models import Portfolio, StockConsolidated, StockPosition, StockSummary, \
    StockPositionMonthlySummary
from goatcommons.portfolio.utils import create_stock_position_wrapper_list, group_stock_position_per_month
from goatcommons.utils import InvestmentUtils
from model import InvestmentRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PortfolioCore:
    def __init__(self, repo):
        self.repo = repo

    def consolidate_portfolio(self, subject, new_investments, old_investments):
        self._invert_investments_list(old_investments)
        portfolio = self.repo.find(subject)

        for current_ticker, investments in self._group_by_current_ticker_name(new_investments + old_investments):
            consolidated_list = self.repo.find_alias_ticker(subject, current_ticker)

            for ticker, t_investments in groupby(sorted(list(investments), key=lambda i: i.ticker),
                                                 key=lambda i: i.ticker):
                consolidated = self._find_ticker_in_consolidated_list(ticker, subject, consolidated_list)

                for inv in sorted(list(t_investments), key=lambda i: i.date):
                    if inv.operation in [OperationType.INCORP_ADD, OperationType.INCORP_SUB]:
                        self._remove_ticker_from_portfolio_summary(ticker, portfolio)
                    if inv.amount > 0:
                        portfolio.initial_date = min(portfolio.initial_date, inv.date)
                    self._consolidate_stock(consolidated, inv)
                self.repo.save(consolidated)
            self._consolidate_portfolio_stock(current_ticker, portfolio,
                                              sum(consolidated_list[1:], consolidated_list[0]))
        self.repo.save(portfolio)

    @staticmethod
    def _remove_ticker_from_portfolio_summary(ticker, portfolio):
        results = list(filter(lambda s: s.ticker == ticker, portfolio.stocks))
        if results:
            logger.info(f'Removing {ticker} from portfoio summary.')
            portfolio.stocks.remove(results[0])

    @staticmethod
    def _find_ticker_in_consolidated_list(ticker, subject, consolidated_list):
        consolidated = next(
            (stock for stock in consolidated_list if stock.ticker == ticker or stock.alias_ticker == ticker),
            None)
        if not consolidated:
            consolidated = StockConsolidated(subject=subject, ticker=ticker)
            consolidated_list.append(consolidated)

        return consolidated

    @staticmethod
    def _group_by_current_ticker_name(investments):
        by_ticker = groupby(sorted(investments, key=lambda i: i.ticker), key=lambda i: i.ticker)
        for ticker, t_investments in by_ticker:
            t_investments = list(t_investments)
            alias_ticker = next((i.alias_ticker for i in t_investments if i.alias_ticker), None)
            if alias_ticker:
                for i in t_investments:
                    i.alias_ticker = alias_ticker
        return groupby(sorted(investments, key=lambda i: i.current_ticker_name), key=lambda i: i.current_ticker_name)

    @staticmethod
    def _invert_investments_list(investments):
        for i in investments:
            i.amount *= -1
        return investments

    @staticmethod
    def _consolidate_portfolio_stock(ticker: str, portfolio: Portfolio, stock_consolidated: StockConsolidated):
        monthly_positions = group_stock_position_per_month(sorted(stock_consolidated.history, key=lambda h: h.date))
        wrapper = create_stock_position_wrapper_list(monthly_positions)
        if wrapper.tail is None:
            return
        current = wrapper.tail
        previous = current.prev

        latest_position = StockPositionMonthlySummary(date=current.data.date, amount=current.amount,
                                                      invested_value=current.current_invested_value,
                                                      bought_value=current.data.bought_value,
                                                      average_price=current.average_price)
        previous_position = None
        if previous:
            previous_position = StockPositionMonthlySummary(date=previous.data.date, amount=previous.amount)

        stock_summary = next(
            (stock for stock in portfolio.stocks if stock.ticker == ticker or stock.alias_ticker == ticker), None)
        if stock_summary:
            stock_summary.ticker = stock_consolidated.ticker
            stock_summary.alias_ticker = stock_consolidated.alias_ticker
            stock_summary.latest_position = latest_position
            stock_summary.previous_position = previous_position
        else:
            stock_summary = StockSummary(stock_consolidated.ticker, alias_ticker=stock_consolidated.alias_ticker,
                                         latest_position=latest_position, previous_position=previous_position)
            portfolio.stocks.append(stock_summary)

    @staticmethod
    def _consolidate_stock(stock_consolidated: StockConsolidated, inv: StockInvestment):
        stock_consolidated.initial_date = min(stock_consolidated.initial_date, inv.date)
        if inv.alias_ticker:
            stock_consolidated.alias_ticker = inv.alias_ticker

        h_position = next((position for position in stock_consolidated.history if position.date == inv.date), None)
        if not h_position:
            h_position = StockPosition.from_stock_investment(inv)
            stock_consolidated.history.append(h_position)
        else:
            h_position.add_investment(inv)

        if h_position.is_empty():
            stock_consolidated.history.remove(h_position)


class InvestmentCore:
    def __init__(self, repo):
        self.repo = repo

    def get(self, subject, query_params):
        assert subject
        if query_params and 'date' in query_params:
            data = query_params['date'].split('.')
            assert len(data) == 2, 'invalid query param'
            operand = data[0]
            value = int(data[1])
            assert operand in ['gt', 'ge', 'lt', 'le', 'eq']
            return self.repo.find_by_subject_and_date(subject, operand, value)
        return self.repo.find_by_subject(subject)

    def add(self, subject, request: InvestmentRequest):
        assert subject
        investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
        assert investment.date <= datetime.now(tz=timezone.utc), 'invalid date'
        if not investment.id:
            investment.id = str(uuid4())
        investment.subject = subject

        self.repo.save(investment)
        return investment

    def edit(self, subject, request: InvestmentRequest):
        assert subject
        investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
        investment.subject = subject
        assert investment.id, 'investment id is empty'
        assert investment.date <= datetime.now(tz=timezone.utc), 'invalid date'

        self.repo.save(investment)
        return investment

    def delete(self, subject, investment_id):
        assert subject
        assert investment_id, 'investment id is empty'

        self.repo.delete(investment_id, subject)

    def batch_add(self, requests: [InvestmentRequest]):
        investments = []
        for request in requests:
            investment = InvestmentUtils.load_model_by_type(request.type, request.investment)
            assert investment.subject, 'subject is empty'
            assert investment.id, 'investment id is empty'

            investments.append(investment)
        self.repo.batch_save(investments)


def main():
    subject = '41e4a793-3ef5-4413-82e2-80919bce7c1a'
    core = PortfolioCore(repo=PortfolioRepository())
    investments = InvestmentRepository().find_by_subject(subject)
    response = core.consolidate_portfolio(subject, investments, [])
    print(response)


if __name__ == '__main__':
    main()
