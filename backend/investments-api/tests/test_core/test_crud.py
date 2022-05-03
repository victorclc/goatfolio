import datetime
import unittest
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from application.paginated_investments_result import PaginatedInvestmentsResult
from core.crud import InvestmentCore
from application.exceptions import FieldMissingError, FieldNotPermittedError, InvalidTicker, InvalidInvestmentDateError
from application.investment_loader import MissingRequiredFields
from application.investment_request import InvestmentRequest
from application.investment_type import InvestmentType
from application.operation_type import OperationType


class TestInvestmentCore(unittest.TestCase):
    def setUp(self):
        self.core = InvestmentCore(repo=MagicMock(), publisher=MagicMock(), ticker=MagicMock())
        self.core.repo.save = MagicMock(return_value=None)
        self.core.repo.batch_save = MagicMock(return_value=None)
        self.core.repo.delete = MagicMock(return_value=None)
        self.core.ticker_client.is_ticker_valid = MagicMock(return_value=True)

    def test_add_stock_investment_with_required_fields_should_save_in_database_and_return_the_updated_investment(
            self,
    ):
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "broker": "INTER",
                "date": "20210101",
                "amount": Decimal(100),
                "price": Decimal(50.5),
                "ticker": "BIDI11",
            },
        )
        result = self.core.add(subject="1111-2222-333-4444", request=request)

        self.core.repo.save.assert_called_once()
        self.assertEqual(result.subject, "1111-2222-333-4444")
        self.assertTrue(result.id)

    def test_add_stock_investment_with_missing_required_fields_should_not_save_in_database_and_raise_exception(
            self,
    ):
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "ticker": "BIDI11",
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5),
            },
        )

        with self.assertRaises(TypeError):
            self.core.add(subject="1111-2222-333-4444", request=request)
        self.core.repo.save.assert_not_called()

    def test_edit_stock_investment_with_all_required_fields_plus_id_should_save_in_database(
            self,
    ):
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5),
                "ticker": "BIDI11",
                "id": "123456",
            },
        )

        result = self.core.edit(subject="1111-2222-333-4444", request=request)

        self.core.repo.save.assert_called_once()
        self.assertEqual(result.subject, "1111-2222-333-4444")
        self.assertEqual(result.id, request.investment["id"])

    def test_edit_stock_investment_with_all_required_fields_minus_id_should_not_save_and_raise_exception(
            self,
    ):
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5),
                "ticker": "BIDI11",
            },
        )
        with self.assertRaises(FieldMissingError):
            self.core.edit(subject="1111-2222-333-4444", request=request)

        self.core.repo.save.assert_not_called()

    def test_delete_investment_with_investment_id_not_blank_should_delete_from_database(
            self,
    ):
        self.core.delete(subject="1111-2222-333-4444", investment_id="123456")
        self.core.repo.delete.assert_called_once()

    def test_delete_investment_with_investment_id_blank_should_raise_exception(self):
        with self.assertRaises(FieldMissingError):
            self.core.delete(subject="1111-2222-333-4444", investment_id="")

        self.core.repo.save.assert_not_called()

    def test_batch_add_with_valid_investments_should_save_in_database(self):
        subject = "1111-2222-3333-4444"
        requests = [
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
        ]
        self.core.batch_add(requests=requests)

        self.core.repo.batch_save.assert_called_once()

    def test_batch_add_with_invalid_investments_should_raise_assertion_error_and_not_save_in_database(
            self,
    ):
        requests = [
            self._create_valid_investment_request_with_subject_and_id(None, None),
            self._create_valid_investment_request_with_subject_and_id(None, None),
            self._create_valid_investment_request_with_subject_and_id(None, None),
        ]
        with self.assertRaises(MissingRequiredFields):
            self.core.batch_add(requests=requests)

        self.core.repo.batch_save.assert_not_called()

    def test_batch_add_with_valid_and_invalid_investments_should_raise_assertion_error_and_not_save_in_database(
            self,
    ):
        subject = "1111-2222-3333-4444"
        requests = [
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
            self._create_valid_investment_request_with_subject_and_id(None, None),
            self._create_valid_investment_request_with_subject_and_id(subject, uuid4()),
        ]
        with self.assertRaises(MissingRequiredFields):
            self.core.batch_add(requests=requests)

        self.core.repo.batch_save.assert_not_called()

    def _create_valid_investment_request_with_subject_and_id(self, subject, _id):
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5),
                "ticker": "BIDI11",
                "subject": subject,
                "id": _id,
            },
        )
        return request

    def test_add_stock_investment_with_an_id_should_not_save_in_database_and_raise_exception(
            self,
    ):
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "ticker": "BIDI11",
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5),
                "id": "1234"
            },
        )

        with self.assertRaises(FieldNotPermittedError):
            self.core.add(subject="1111-2222-333-4444", request=request)
        self.core.repo.save.assert_not_called()

    def test_add_not_mapped_investment_type_should_raise_exception(
            self,
    ):
        request = InvestmentRequest(
            type=InvestmentType.POST_FIXED,
            investment={
                "ticker": "BIDI11",
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5)
            },
        )

        with self.assertRaises(TypeError):
            self.core.add(subject="1111-2222-333-4444", request=request)
        self.core.repo.save.assert_not_called()

    def test_get_investments_without_pagination_data_should_return_a_list_of_investments(self):
        self.core.repo.find_by_subject = MagicMock(return_value=([], None, None))

        response = self.core.get("1111-2222-3333-444")

        self.assertTrue(isinstance(response, list))


    def test_get_investments_with_pagination_data_should_return_a_paginated_investments_result(self):
        self.core.repo.find_by_subject = MagicMock(return_value=([], None, None))

        response = self.core.get("1111-2222-3333-444", limit=20)

        self.assertTrue(isinstance(response, PaginatedInvestmentsResult))


    def test_add_invalid_ticker_should_raise_exception(
            self,
    ):
        self.core.ticker_client.is_ticker_valid = MagicMock(return_value=False)
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "ticker": "BIDI11X",
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5)
            },
        )

        with self.assertRaises(InvalidTicker):
            self.core.add(subject="1111-2222-333-4444", request=request)
        self.core.repo.save.assert_not_called()

    def test_add_invalid_ticker_should_raise_exception(
            self,
    ):
        self.core.ticker_client.is_ticker_valid = MagicMock(return_value=False)
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "ticker": "BIDI11X",
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5)
            },
        )

        with self.assertRaises(InvalidTicker):
            self.core.add(subject="1111-2222-333-4444", request=request)
        self.core.repo.save.assert_not_called()

    def test_add_future_date_should_raise_exception(
            self,
    ):
        self.core.ticker_client.is_ticker_valid = MagicMock(return_value=False)
        request = InvestmentRequest(
            type=InvestmentType.STOCK,
            investment={
                "operation": OperationType.BUY,
                "ticker": "BIDI11X",
                "broker": "INTER",
                "date": datetime.date.max,
                "amount": Decimal(100),
                "price": Decimal(50.5)
            },
        )

        with self.assertRaises(InvalidInvestmentDateError):
            self.core.add(subject="1111-2222-333-4444", request=request)
        self.core.repo.save.assert_not_called()

