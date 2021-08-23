import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

from core import PerformanceCore
from goatcommons.constants import OperationType
from goatcommons.models import StockInvestment
from models import Portfolio, StockConsolidated, StockPosition


class TestPerformanceCore(unittest.TestCase):
    def setUp(self):
        self.core = PerformanceCore(repo=MagicMock(), market_data=MagicMock())
        self.core.repo.find = MagicMock(return_value=None)
        self.core.repo.save = MagicMock(return_value=None)

    # add multiple investment in different dates, must create multiple amount of StockPosition
    def test_new_buy_investment_with_no_portfolio_on_database_should_create_an_empty_portfolio_add_an_stock_position_object_and_persist_on_database(
            self):
        initial_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        investment = StockInvestment(Decimal(100), Decimal('15.50'), 'BIDI11', OperationType.BUY, initial_date, 'STOCK',
                                     'Inter')
        self.core.repo.find = MagicMock(return_value=None)

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertEqual(portfolio.initial_date, initial_date, 'Initial date doesnt match')
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        self.assertEqual(portfolio.stocks[0].initial_date, initial_date, 'Stock initial date doesnt match')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, initial_date)
        self.assertEqual(position.bought_amount, investment.amount)
        self.assertEqual(position.bought_value, investment.amount * investment.price)
        self.assertEqual(position.sold_amount, 0)
        self.assertEqual(position.sold_value, 0)

    def test_new_sell_investment_with_no_portfolio_on_database_should_create_an_empty_portfolio_add_an_stock_position_object_and_persist_on_database(
            self):
        initial_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        investment = StockInvestment(Decimal(100), Decimal('15.50'), 'BIDI11', OperationType.SELL, initial_date,
                                     'STOCK', 'Inter')
        self.core.repo.find = MagicMock(return_value=None)

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertEqual(portfolio.initial_date, initial_date, 'Initial date doesnt match')
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        self.assertEqual(portfolio.stocks[0].initial_date, initial_date, 'Stock initial date doesnt match')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, initial_date)
        self.assertEqual(position.bought_amount, 0)
        self.assertEqual(position.bought_value, 0)
        self.assertEqual(position.sold_amount, investment.amount)
        self.assertEqual(position.sold_value, investment.amount * investment.price)

    def test_new_split_investment_with_no_portfolio_on_database_should_create_an_empty_portfolio_add_an_stock_position_object_and_persist_on_database(
            self):
        initial_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        investment = StockInvestment(Decimal(100), Decimal('0'), 'BIDI11', OperationType.SPLIT, initial_date, 'STOCK',
                                     'Inter')
        self.core.repo.find = MagicMock(return_value=None)

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertEqual(portfolio.initial_date, initial_date, 'Initial date doesnt match')
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        self.assertEqual(portfolio.stocks[0].initial_date, initial_date, 'Stock initial date doesnt match')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, initial_date)
        self.assertEqual(position.bought_amount, investment.amount)
        self.assertEqual(position.bought_value, investment.amount * investment.price)
        self.assertEqual(position.sold_amount, 0)
        self.assertEqual(position.sold_value, 0)

    def test_new_group_investment_with_no_portfolio_on_database_should_create_an_empty_portfolio_add_an_stock_position_object_and_persist_on_database(
            self):
        initial_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        investment = StockInvestment(Decimal(100), Decimal('0'), 'BIDI11', OperationType.GROUP, initial_date,
                                     'STOCK', 'Inter')
        self.core.repo.find = MagicMock(return_value=None)

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertEqual(portfolio.initial_date, initial_date, 'Initial date doesnt match')
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        self.assertEqual(portfolio.stocks[0].initial_date, initial_date, 'Stock initial date doesnt match')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, initial_date)
        self.assertEqual(position.bought_amount, 0)
        self.assertEqual(position.bought_value, 0)
        self.assertEqual(position.sold_amount, investment.amount)
        self.assertEqual(position.sold_value, investment.amount * investment.price)

    def test_new_incorp_add_investment_with_no_portfolio_on_database_should_create_an_empty_portfolio_add_an_stock_position_object_and_persist_on_database(
            self):
        initial_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        investment = StockInvestment(Decimal(100), Decimal('0'), 'BIDI11', OperationType.INCORP_ADD, initial_date,
                                     'STOCK', 'Inter')
        self.core.repo.find = MagicMock(return_value=None)

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertEqual(portfolio.initial_date, initial_date, 'Initial date doesnt match')
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        self.assertEqual(portfolio.stocks[0].initial_date, initial_date, 'Stock initial date doesnt match')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, initial_date)
        self.assertEqual(position.bought_amount, investment.amount)
        self.assertEqual(position.bought_value, investment.amount * investment.price)
        self.assertEqual(position.sold_amount, 0)
        self.assertEqual(position.sold_value, 0)

    def test_new_incorp_sub_investment_with_no_portfolio_on_database_should_create_an_empty_portfolio_add_an_stock_position_object_and_persist_on_database(
            self):
        initial_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        investment = StockInvestment(Decimal(100), Decimal('0'), 'BIDI11', OperationType.INCORP_SUB, initial_date,
                                     'STOCK', 'Inter')
        self.core.repo.find = MagicMock(return_value=None)

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertEqual(portfolio.initial_date, initial_date, 'Initial date doesnt match')
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        self.assertEqual(portfolio.stocks[0].initial_date, initial_date, 'Stock initial date doesnt match')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, initial_date)
        self.assertEqual(position.bought_amount, 0)
        self.assertEqual(position.bought_value, 0)
        self.assertEqual(position.sold_amount, investment.amount)
        self.assertEqual(position.sold_value, investment.amount * investment.price)

    def test_new_buy_investment_with_the_same_date_of_position_on_user_portfolio_should_add_investment_date_with_the_position_and_persist_on_database(
            self):
        investment_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        repo_portfolio = Portfolio('1111-2222-3333-4444', investment_date,
                                   [StockConsolidated('BIDI11', initial_date=investment_date, history=[
                                       StockPosition(investment_date, Decimal(0), Decimal(100), Decimal(10000),
                                                     Decimal(0)).to_dict()]).to_dict()])

        self.core.repo.find = MagicMock(return_value=repo_portfolio)
        investment = StockInvestment(Decimal(100), Decimal('15.50'), 'BIDI11', OperationType.BUY, investment_date,
                                     'STOCK', 'Inter')

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])
        self.core.repo.save.assert_called_once()
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 1, 'Unexpected stock history length')
        position = portfolio.stocks[0].history[0]
        self.assertEqual(position.date, investment_date)
        self.assertEqual(position.bought_amount, 100 + investment.amount)
        self.assertEqual(position.bought_value, 10000 + investment.amount * investment.price)
        self.assertEqual(position.sold_amount, 0)
        self.assertEqual(position.sold_value, 0)

    def test_new_buy_investment_with_different_date_of_position_on_user_portfolio_should_create_new_stock_position_and_persist_on_database(
            self):
        investment_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        repo_portfolio = Portfolio('1111-2222-3333-4444', investment_date,
                                   [StockConsolidated('BIDI11', initial_date=investment_date,
                                                      history=[StockPosition(investment_date, Decimal(0), Decimal(100),
                                                                             Decimal(10000),
                                                                             Decimal(0)).to_dict()]).to_dict()])

        self.core.repo.find = MagicMock(return_value=repo_portfolio)
        investment = StockInvestment(Decimal(100), Decimal('15.50'), 'BIDI11', OperationType.BUY,
                                     datetime(2021, 5, 13, tzinfo=timezone.utc), 'STOCK', 'Inter')

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [investment], [])

        self.core.repo.save.assert_called_once()
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 2, 'Unexpected stock history length')
        prev_position = portfolio.stocks[0].history[0]
        new_position = portfolio.stocks[0].history[1]
        self.assertEqual(prev_position.date, investment_date)
        self.assertEqual(prev_position, repo_portfolio.stocks[0].history[0])
        self.assertEqual(new_position.date, investment.date)
        self.assertEqual(new_position.bought_amount, investment.amount)
        self.assertEqual(new_position.bought_value, investment.amount * investment.price)
        self.assertEqual(new_position.sold_amount, 0)
        self.assertEqual(new_position.sold_value, 0)

    def test_old_investment_with_same_data_from_stock_position_in_portfolio_should_remove_stock_position_from_portfolio_and_persist_on_database(
            self):
        investment_date = datetime(2021, 5, 12, tzinfo=timezone.utc)
        repo_portfolio = Portfolio('1111-2222-3333-4444', investment_date,
                                   [StockConsolidated('BIDI11', initial_date=investment_date,
                                                      history=[StockPosition(investment_date, Decimal(0), Decimal(100),
                                                                             Decimal(10000),
                                                                             Decimal(0)).to_dict()]).to_dict()])

        self.core.repo.find = MagicMock(return_value=repo_portfolio)
        investment = StockInvestment(Decimal(100), Decimal(100), 'BIDI11', OperationType.BUY, investment_date,
                                     'STOCK', 'Inter')

        portfolio = self.core.consolidate_portfolio('1111-2222-3333-4444', [], [investment])

        self.core.repo.save.assert_called_once()
        self.assertTrue(len(portfolio.stocks) == 1, 'Unexpected stocks length')
        self.assertTrue(len(portfolio.stocks[0].history) == 0, 'Unexpected stock history length')
