import unittest
from dataclasses import asdict
from decimal import Decimal
from unittest.mock import MagicMock

import core
from constants import ImportStatus
from exceptions import UnprocessableException, BatchSavingException

from models import CEIInboundRequest, Import, CEIImportResult, StockInvestment, OperationType


class TestCEICore(unittest.TestCase):
    def setUp(self):
        self.core = core.CEICore(
            repo=MagicMock(),
            queue=MagicMock(),
            portfolio=MagicMock(),
            push=MagicMock(),
            cei_repo=MagicMock(),
        )
        self.core.repo.send = MagicMock(return_value=None)
        self.core.repo.find_latest = MagicMock(return_value=None)
        self.core.repo.find = MagicMock(return_value=None)
        self.core.queue.send = MagicMock(return_value=None)
        self.core.portfolio.batch_save = MagicMock(return_value=None)
        self.valid_request = CEIInboundRequest(
            tax_id="12345678909", password="123456@A"
        )
        self.invalid_tax_id_request = CEIInboundRequest(
            tax_id="12345678999", password="123456@A"
        )
        self.invalid_password_request = CEIInboundRequest(
            tax_id="12345678909", password="12345678"
        )
        self.invalid_tax_id_and_password_request = CEIInboundRequest(
            tax_id="12345678999", password="12345678"
        )
        self.core.push.send_message = MagicMock(return_value=None)

    def test_request_with_valid_tax_id_and_password_with_no_open_imports_should_save_on_database_and_send_to_queue(
        self,
    ):
        self.core.import_request(
            subject="1111-2222-333-4444", request=self.valid_request
        )

        self.core.repo.send.assert_called_once()
        self.core.queue.send.assert_called_once()

    def test_request_with_valid_tax_id_and_password_with_successful_prev_import_should_save_on_database_and_send_to_queue(
        self,
    ):
        latest = Import(
            subject="1111-2222-333-4444",
            datetime=123,
            username="12345678909",
            status=ImportStatus.SUCCESS,
        )
        self.core.repo.find_latest = MagicMock(return_value=latest)

        self.core.import_request(
            subject="1111-2222-333-4444", request=self.valid_request
        )

        self.core.repo.send.assert_called_once()
        self.core.queue.send.assert_called_once()

    def test_request_with_valid_tax_id_and_password_with_error_prev_import_should_save_on_database_and_send_to_queue(
        self,
    ):
        latest = Import(
            subject="1111-2222-333-4444",
            datetime=123,
            username="12345678909",
            status=ImportStatus.ERROR,
        )
        self.core.repo.find_latest = MagicMock(return_value=latest)

        self.core.import_request(
            subject="1111-2222-333-4444", request=self.valid_request
        )

        self.core.repo.send.assert_called_once()
        self.core.queue.send.assert_called_once()

    def test_request_with_valid_tax_id_and_password_with_processing_prev_import_should_raise_exception_and_not_save_on_database_or_send_to_queue(
        self,
    ):
        latest = Import(
            subject="1111-2222-333-4444",
            datetime=123,
            username="12345678909",
            status=ImportStatus.PROCESSING,
        )
        self.core.repo.find_latest = MagicMock(return_value=latest)

        with self.assertRaises(UnprocessableException):
            self.core.import_request(
                subject="1111-2222-333-4444", request=self.valid_request
            )
        self.core.repo.send.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_request_with_invalid_tax_id_and_valid_password_should_raise_exception_and_not_save_on_database_or_send_to_queue(
        self,
    ):
        with self.assertRaises(UnprocessableException):
            self.core.import_request(
                subject="1111-2222-333-4444", request=self.invalid_tax_id_request
            )
        self.core.repo.send.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_request_with_valid_tax_id_and_invalid_password_should_raise_exception_and_not_save_on_database_or_send_to_queue(
        self,
    ):
        with self.assertRaises(UnprocessableException):
            self.core.import_request(
                subject="1111-2222-333-4444", request=self.invalid_password_request
            )
        self.core.repo.send.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_request_with_invalid_tax_id_and_password_should_raise_exception_and_not_save_on_database_or_send_to_queue(
        self,
    ):
        with self.assertRaises(UnprocessableException):
            self.core.import_request(
                subject="1111-2222-333-4444",
                request=self.invalid_tax_id_and_password_request,
            )
        self.core.repo.send.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_successful_import_result_should_update_the_status_and_payload_on_database_and_call_batch_save(
        self,
    ):
        payload = {
            "investments": list(
                map(lambda _: asdict(self._create_stock_investment()), range(10))
            ),
            "assets_quantities": {"BIDI11": 100},
        }
        import_result = CEIImportResult(
            subject="1111-2222-333-4444",
            datetime=123,
            status=ImportStatus.SUCCESS,
            payload=payload,
        )

        self.core.repo.find.return_value = Import(
            subject="1111-2222-333-4444",
            datetime=123,
            username="12345678909",
            status=ImportStatus.PROCESSING,
        )
        result = self.core.import_result(result=import_result)

        self.core.portfolio.batch_save.assert_called_once()
        self.core.repo.send.assert_called_once()
        self.core.info_queue.send.assert_called_once()
        self.assertEqual(result.status, import_result.status)
        self.assertEqual(result.payload, import_result.payload)
        self.assertIsNone(result.error_message)

    def test_not_successful_import_result_should_update_the_status_and_payload_and_error_message_on_database(
        self,
    ):
        import_result = CEIImportResult(
            subject="1111-2222-333-4444",
            datetime=123,
            status=ImportStatus.ERROR,
            payload="Some error here",
        )

        self.core.repo.find.return_value = Import(
            subject="1111-2222-333-4444",
            datetime=123,
            username="12345678909",
            status=ImportStatus.PROCESSING,
        )
        result = self.core.import_result(result=import_result)

        self.core.portfolio.batch_save.assert_not_called()
        self.core.repo.send.assert_called_once()
        self.assertEqual(result.status, import_result.status)
        self.assertEqual(result.payload, import_result.payload)
        self.assertEqual(result.error_message, import_result.payload)

    def test_successful_import_result_when_error_on_call_batch_save_should_update_status_to_error_and_set_error_message(
        self,
    ):
        payload = {
            "investments": list(
                map(lambda _: asdict(self._create_stock_investment()), range(10))
            )
        }
        import_result = CEIImportResult(
            subject="1111-2222-333-4444",
            datetime=123,
            status=ImportStatus.SUCCESS,
            payload=payload,
        )

        self.core.repo.find.return_value = Import(
            subject="1111-2222-333-4444",
            datetime=123,
            username="12345678909",
            status=ImportStatus.PROCESSING,
        )
        self.core.portfolio.batch_save.side_effect = BatchSavingException()
        result = self.core.import_result(result=import_result)

        self.core.portfolio.batch_save.assert_called_once()
        self.core.repo.send.assert_called_once()
        self.assertEqual(result.status, ImportStatus.ERROR)
        self.assertEqual(result.payload, import_result.payload)
        self.assertIsNotNone(result.error_message)

    def _create_stock_investment(self):
        return StockInvestment(
            **{
                "operation": OperationType.BUY,
                "type": "STOCK",
                "broker": "INTER",
                "date": "123456",
                "amount": Decimal(100),
                "price": Decimal(50.5),
                "ticker": "BIDI11",
                "subject": "1111-2222-3333-4444",
                "id": "12345",
            }
        )


if __name__ == "__main__":
    unittest.main()
