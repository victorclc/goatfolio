import unittest
from unittest.mock import MagicMock

import core
from constants import ImportStatus
from exceptions import UnprocessableException
from models import CEIInboundRequest, Import


class TestCEICore(unittest.TestCase):
    def setUp(self):
        self.core = core.CEICore()
        self.core.repo.save = MagicMock(return_value=None)
        self.core.repo.find_latest = MagicMock(return_value=None)
        self.core.queue.send = MagicMock(return_value=None)
        self.valid_request = CEIInboundRequest(tax_id='12345678909', password='123456@A')
        self.invalid_tax_id_request = CEIInboundRequest(tax_id='12345678999', password='123456@A')
        self.invalid_password_request = CEIInboundRequest(tax_id='12345678909', password='12345678')
        self.invalid_tax_id_and_password_request = CEIInboundRequest(tax_id='12345678999', password='12345678')

    def test_request_with_valid_tax_id_and_password_with_no_open_imports_should_save_on_database_and_send_to_queue(
            self):
        self.core.import_request(subject='1111-2222-333-4444', request=self.valid_request)

        self.core.repo.save.assert_called_once()
        self.core.queue.send.assert_called_once()

    def test_request_with_valid_tax_id_and_password_with_successful_prev_import_should_save_on_database_and_send_to_queue(
            self):
        latest = Import(subject='1111-2222-333-4444', datetime=123, username='12345678909', status=ImportStatus.SUCCESS)
        self.core.repo.find_latest = MagicMock(return_value=latest)

        self.core.import_request(subject='1111-2222-333-4444', request=self.valid_request)

        self.core.repo.save.assert_called_once()
        self.core.queue.send.assert_called_once()

    def test_request_with_valid_tax_id_and_password_with_error_prev_import_should_save_on_database_and_send_to_queue(
            self):
        latest = Import(subject='1111-2222-333-4444', datetime=123, username='12345678909', status=ImportStatus.ERROR)
        self.core.repo.find_latest = MagicMock(return_value=latest)

        self.core.import_request(subject='1111-2222-333-4444', request=self.valid_request)

        self.core.repo.save.assert_called_once()
        self.core.queue.send.assert_called_once()

    def test_request_with_valid_tax_id_and_password_with_processing_prev_import_should_raise_exception_and_not_save_on_database_or_send_to_queue(
            self):
        latest = Import(subject='1111-2222-333-4444', datetime=123, username='12345678909',
                        status=ImportStatus.PROCESSING)
        self.core.repo.find_latest = MagicMock(return_value=latest)

        with self.assertRaises(UnprocessableException):
            self.core.import_request(subject='1111-2222-333-4444', request=self.valid_request)
        self.core.repo.save.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_request_with_invalid_tax_id_and_valid_password_should_raise_exception_and_not_save_on_database_or_send_to_queue(
            self):
        with self.assertRaises(UnprocessableException):
            self.core.import_request(subject='1111-2222-333-4444', request=self.invalid_tax_id_request)
        self.core.repo.save.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_request_with_valid_tax_id_and_invalid_password_should_raise_exception_and_not_save_on_database_or_send_to_queue(
            self):
        with self.assertRaises(UnprocessableException):
            self.core.import_request(subject='1111-2222-333-4444', request=self.invalid_password_request)
        self.core.repo.save.assert_not_called()
        self.core.queue.send.assert_not_called()

    def test_request_with_invalid_tax_id_and_password_should_raise_exception_and_not_save_on_database_or_send_to_queue(
            self):
        with self.assertRaises(UnprocessableException):
            self.core.import_request(subject='1111-2222-333-4444', request=self.invalid_tax_id_and_password_request)
        self.core.repo.save.assert_not_called()
        self.core.queue.send.assert_not_called()


if __name__ == '__main__':
    unittest.main()
