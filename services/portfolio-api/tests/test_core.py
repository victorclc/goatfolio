import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import core
from goatcommons.constants import InvestmentsType, OperationType
from goatcommons.models import StockInvestment
from goatcommons.portfolio.models import Portfolio, StockConsolidated, StockPosition, StockSummary, \
    StockPositionMonthlySummary
from model import InvestmentRequest


class TestInvestmentCore(unittest.TestCase):
    def setUp(self):
        self.core = core.InvestmentCore(repo=MagicMock())
        self.core.repo.save = MagicMock(return_value=None)
        self.core.repo.batch_save = MagicMock(return_value=None)
        self.core.repo.delete = MagicMock(return_value=None)

    def test_add_stock_investment_with_required_fields_should_save_in_database_and_return_the_updated_investment(self):
        request = InvestmentRequest(type=InvestmentsType.STOCK, investment={
            'operation': OperationType.BUY,
            'broker': 'INTER',
            'date': '123456',
            'amount': Decimal(100),
            'price': Decimal(50.5),
            'ticker': 'BIDI11',
        })
        result = self.core.add(subject='1111-2222-333-4444', request=request)

        self.core.repo.save.assert_called_once()
        self.assertEqual(result.subject, '1111-2222-333-4444')
        self.assertTrue(result.id)

    def test_add_stock_investment_with_missing_required_fields_should_not_save_in_database_and_raise_exception(self):
        request = InvestmentRequest(type=InvestmentsType.STOCK, investment={
            'operation': OperationType.BUY,
            'broker': 'INTER',
            'date': '123456',
            'amount': Decimal(100),
            'price': Decimal(50.5),
        })

        with self.assertRaises(TypeError):
            self.core.add(subject='1111-2222-333-4444', request=request)
        self.core.repo.save.assert_not_called()

    def test_edit_stock_investment_with_all_required_fields_plus_id_should_save_in_database(self):
        request = InvestmentRequest(type=InvestmentsType.STOCK, investment={
            'operation': OperationType.BUY,
            'broker': 'INTER',
            'date': '123456',
            'amount': Decimal(100),
            'price': Decimal(50.5),
            'ticker': 'BIDI11',
            'id': '123456'
        })

        result = self.core.edit(subject='1111-2222-333-4444', request=request)

        self.core.repo.save.assert_called_once()
        self.assertEqual(result.subject, '1111-2222-333-4444')
        self.assertEqual(result.id, request.investment['id'])

    def test_edit_stock_investment_with_all_required_fields_minus_id_should_not_save_and_raise_exception(self):
        request = InvestmentRequest(type=InvestmentsType.STOCK, investment={
            'operation': OperationType.BUY,
            'broker': 'INTER',
            'date': '123456',
            'amount': Decimal(100),
            'price': Decimal(50.5),
            'ticker': 'BIDI11',
        })
        with self.assertRaises(AssertionError):
            self.core.edit(subject='1111-2222-333-4444', request=request)

        self.core.repo.save.assert_not_called()

    def test_delete_investment_with_investment_id_not_blank_should_delete_from_database(self):
        self.core.delete(subject='1111-2222-333-4444', investment_id='123456')
        self.core.repo.delete.assert_called_once()

    def test_delete_investment_with_investment_id_blank_should_raise_exception(self):
        with self.assertRaises(AssertionError):
            self.core.delete(subject='1111-2222-333-4444', investment_id='')

        self.core.repo.save.assert_not_called()

    def test_batch_add_with_valid_investments_should_save_in_database(self):
        subject = '1111-2222-3333-4444'
        requests = [
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4())
        ]
        self.core.batch_add(requests=requests)

        self.core.repo.batch_save.assert_called_once()

    def test_batch_add_with_invalid_investments_should_raise_assertion_error_and_not_save_in_database(self):
        requests = [
            self._create_valid_investment_request_with_subject_and_id(None, None),
            self._create_valid_investment_request_with_subject_and_id(None, None),
            self._create_valid_investment_request_with_subject_and_id(None, None)
        ]
        with self.assertRaises(AssertionError):
            self.core.batch_add(requests=requests)

        self.core.repo.batch_save.assert_not_called()

    def test_batch_add_with_valid_and_invalid_investments_should_raise_assertion_error_and_not_save_in_database(self):
        subject = '1111-2222-3333-4444'
        requests = [
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
            self._create_valid_investment_request_with_subject_and_id(None, None),
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4())
        ]
        with self.assertRaises(AssertionError):
            self.core.batch_add(requests=requests)

        self.core.repo.batch_save.assert_not_called()

    def _create_valid_investment_request_with_subject_and_id(self, subject, _id):
        request = InvestmentRequest(type=InvestmentsType.STOCK, investment={
            'operation': OperationType.BUY,
            'broker': 'INTER',
            'date': '123456',
            'amount': Decimal(100),
            'price': Decimal(50.5),
            'ticker': 'BIDI11',
            'subject': subject,
            'id': _id
        })
        return request


class TestPortfolioCore(unittest.TestCase):
    def setUp(self):
        self.core = core.PortfolioCore(repo=MagicMock())
        self.BUY_INVESTMENT = StockInvestment(Decimal(100), Decimal('15.50'), 'BIDI11', OperationType.BUY,
                                              datetime(2021, 5, 12, tzinfo=timezone.utc), 'STOCK', 'Inter')
        self.subject = '1111-2222-3333-4444'

    def test_one_new_investment_without_an_portfolio_should_persis_an_portfolio_and_an_stock_consolidated_objects(self):
        self.core.repo.find = MagicMock(return_value=None)
        self.core.repo.find_ticker = MagicMock(return_value=None)
        self.core.repo.find_alias_ticker = MagicMock(return_value=None)

        self.core.consolidate_portfolio(self.subject, [self.BUY_INVESTMENT], [])

        save_args = self.core.repo.save.call_args_list
        stock_consolidated = save_args[0].args[0]
        portfolio = save_args[1].args[0]
        self.assertEqual(self.core.repo.save.call_count, 2)
        self.assertIsInstance(stock_consolidated, StockConsolidated)
        self.assertIsInstance(portfolio, Portfolio)
        self.assertEqual(portfolio.stocks[0].latest_position.amount, self.BUY_INVESTMENT.amount)
        self.assertEqual(portfolio.stocks[0].latest_position.invested_value,
                         self.BUY_INVESTMENT.amount * self.BUY_INVESTMENT.price)
        self.assertIsNone(portfolio.stocks[0].previous_position)
        self.assertEqual(portfolio.initial_date, self.BUY_INVESTMENT.date)

    def test_new_investment_with_an_existing_portfolio_and_existing_stock_consolidated_should_update_latest_and_previous_position_and_consolidate_history(
            self):
        position_summary = StockPositionMonthlySummary(date=datetime(2021, 4, 1, 0, 0, tzinfo=timezone.utc),
                                                       amount=Decimal('100.00'), invested_value=Decimal('1550.00'),
                                                       bought_value=Decimal('1550.00'), average_price=Decimal('15.50'))
        stock_summary = StockSummary(ticker='BIDI11', latest_position=position_summary)
        portfolio = Portfolio(subject=self.subject, ticker=self.subject,
                              initial_date=datetime(2021, 4, 12, 0, 0, tzinfo=timezone.utc), stocks=[stock_summary])
        stock_consolidated = StockConsolidated(subject='1111-2222-3333-4444', ticker='BIDI11', alias_ticker='',
                                               initial_date=datetime(2021, 4, 12, 0, 0, tzinfo=timezone.utc),
                                               history=[
                                                   StockPosition(date=datetime(2021, 4, 12, 0, 0, tzinfo=timezone.utc),
                                                                 bought_amount=Decimal('100.00'),
                                                                 bought_value=Decimal('1550.00'))])

        self.core.repo.find = MagicMock(return_value=portfolio)
        self.core.repo.find_alias_ticker = MagicMock(return_value=[stock_consolidated])

        self.core.consolidate_portfolio(self.subject, [self.BUY_INVESTMENT], [])

        self.assertEqual(self.core.repo.save.call_count, 2)
        self.assertIsNotNone(portfolio.stocks[0].previous_position)
        self.assertEqual(portfolio.stocks[0].latest_position.amount,
                         portfolio.stocks[0].previous_position.amount + self.BUY_INVESTMENT.amount)
        self.assertEqual(len(stock_consolidated.history), 2)

    # def test_bug(self):
    #     new_investments = [StockInvestment(amount=Decimal('16'), price=Decimal('5.55'), ticker='TIET4', operation='BUY',
    #                                        date=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), type='STOCK',
    #                                        broker='Inter', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='5379013d-1bde-489c-8d2f-7d43adb959e3', costs=Decimal('0'),
    #                                        alias_ticker='AESB3'),
    #                        StockInvestment(amount=Decimal('12'), price=Decimal('0'), ticker='TIET4',
    #                                        operation='INCORP_SUB',
    #                                        date=datetime(2021, 3, 27, 0, 0, tzinfo=timezone.utc), type='STOCK',
    #                                        broker='', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='TIET4INCORPORACAO2021012920210326BRAESBACNOR7', costs=Decimal('0'),
    #                                        alias_ticker='AESB3')]
    #     old_investments = [StockInvestment(amount=Decimal('16'), price=Decimal('5.55'), ticker='TIET4', operation='BUY',
    #                                        date=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
    #                                        type='STOCK', broker='Inter', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='5379013d-1bde-489c-8d2f-7d43adb959e3', costs=Decimal('0'),
    #                                        alias_ticker=''),
    #                        StockInvestment(amount=Decimal('0'), price=Decimal('0'), ticker='TIET4',
    #                                        operation='INCORP_SUB',
    #                                        date=datetime(2021, 3, 27, 0, 0, tzinfo=timezone.utc),
    #                                        type='STOCK', broker='', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='TIET4INCORPORACAO2021012920210326BRAESBACNOR7', costs=Decimal('0'),
    #                                        alias_ticker='AESB3')]
    #
    #     self.core.consolidate_portfolio(self.subject, new_investments, old_investments)


    # TODO TEST ALL KINDS OF INVESTMENTS TYPE

    if __name__ == '__main__':
        unittest.main()
