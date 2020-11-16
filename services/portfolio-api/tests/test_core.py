import unittest
from decimal import Decimal
from unittest.mock import MagicMock

import core
from goatcommons.constants import InvestmentsType, OperationType
from model import InvestmentRequest


class TestInvestmentCore(unittest.TestCase):
    def setUp(self):
        self.core = core.InvestmentCore()
        self.core.repo.save = MagicMock(return_value=None)

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

    def test_add_stock_investment_with_required_fields_but_invalid_datatype_should_raise_exception(self):
        request = InvestmentRequest(type=InvestmentsType.STOCK, investment={
            'operation': OperationType.BUY,
            'broker': 'INTER',
            'date': '123456',
            'amount': 100,
            'price': "50.5",
            'ticker': 'BIDI11',
        })
        with self.assertRaises(TypeError):
            self.core.add(subject='1111-2222-333-4444', request=request)
        self.core.repo.save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
