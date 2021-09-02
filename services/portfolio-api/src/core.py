import logging
from datetime import datetime, timezone
from itertools import groupby
from uuid import uuid4

from goatcommons.models import StockInvestment
from goatcommons.portfolio.models import Portfolio, StockConsolidated, StockPosition
from goatcommons.utils import InvestmentUtils
from model import InvestmentRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PortfolioCore:
    def __init__(self, repo):
        self.repo = repo

    def consolidate_portfolio(self, subject, new_investments, old_investments):
        logger.info(f'New investments = {new_investments}')
        logger.info(f'Old investments = {old_investments}')

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
