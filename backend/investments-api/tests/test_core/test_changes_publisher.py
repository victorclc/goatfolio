import unittest
from decimal import Decimal
from unittest.mock import MagicMock

from application.investment import StockInvestment, StockDividend, Investment
from application.investment_type import InvestmentType
from application.operation_type import OperationType
from core import changes_publisher


class TestChangePublisher(unittest.TestCase):
    def setUp(self):
        self.publisher = MagicMock()

    def test_new_stock_investment_should_call_publish_stock_investment_only(
            self,
    ):
        subject = "1111-2222-3333-4444"
        stock_investment = StockInvestment(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.STOCK,
            operation=OperationType.BUY,
            ticker="BIDI11",
            amount=Decimal(100),
            price=Decimal(50),
            broker="INTER"
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, stock_investment, None)
        self.publisher.publish_stock_investment.assert_called_once()
        self.publisher.publish_stock_dividend.assert_not_called()

    def test_old_stock_investment_should_call_publish_stock_investment_only(
            self,
    ):
        subject = "1111-2222-3333-4444"
        stock_investment = StockInvestment(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.STOCK,
            operation=OperationType.BUY,
            ticker="BIDI11",
            amount=Decimal(100),
            price=Decimal(50),
            broker="INTER"
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, None, stock_investment)
        self.publisher.publish_stock_investment.assert_called_once()
        self.publisher.publish_stock_dividend.assert_not_called()

    def test_edit_stock_investment_should_call_publish_stock_investment_only(
            self,
    ):
        subject = "1111-2222-3333-4444"
        stock_investment = StockInvestment(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.STOCK,
            operation=OperationType.BUY,
            ticker="BIDI11",
            amount=Decimal(100),
            price=Decimal(50),
            broker="INTER"
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, stock_investment,
                                                    stock_investment)
        self.publisher.publish_stock_investment.assert_called_once()
        self.publisher.publish_stock_dividend.assert_not_called()

    def test_new_stock_dividend_should_call_publish_stock_dividend_only(
            self,
    ):
        subject = "1111-2222-3333-4444"
        stock_dividend = StockDividend(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.STOCK,
            ticker="BIDI11",
            amount=Decimal(100.55),
            label="DIVIDENDO"
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, stock_dividend, None)
        self.publisher.publish_stock_investment.assert_not_called()
        self.publisher.publish_stock_dividend.assert_called_once()

    def test_old_stock_dividend_should_call_publish_stock_dividend_only(
            self,
    ):
        subject = "1111-2222-3333-4444"
        stock_dividend = StockDividend(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.STOCK,
            ticker="BIDI11",
            amount=Decimal(100.55),
            label="DIVIDENDO"
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, None, stock_dividend)
        self.publisher.publish_stock_investment.assert_not_called()
        self.publisher.publish_stock_dividend.assert_called_once()

    def test_edit_stock_dividend_should_call_publish_stock_dividend_only(
            self,
    ):
        subject = "1111-2222-3333-4444"
        stock_dividend = StockDividend(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.STOCK,
            ticker="BIDI11",
            amount=Decimal(100.55),
            label="DIVIDENDO"
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, stock_dividend, stock_dividend)
        self.publisher.publish_stock_investment.assert_not_called()
        self.publisher.publish_stock_dividend.assert_called_once()

    def test_unknown_investment_should_not_publish_anything(
            self,
    ):
        subject = "1111-2222-3333-4444"

        class UnknownInvestment(Investment):
            def to_json(self):
                pass

        stock_dividend = UnknownInvestment(
            subject=subject,
            id="ID",
            date="20220504",
            type=InvestmentType.CRYPTO,
        )

        changes_publisher.publish_investment_update(self.publisher, subject, 1234567, stock_dividend, stock_dividend)
        self.publisher.publish_stock_investment.assert_not_called()
        self.publisher.publish_stock_dividend.assert_not_called()
