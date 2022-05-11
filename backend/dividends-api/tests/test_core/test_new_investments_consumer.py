import unittest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import MagicMock

from application.models.dividends import CashDividends
from application.models.invesments import StockInvestment, InvestmentType, OperationType, StockDividend
from core.new_investments_consumer import NewInvestmentsConsumer


class TestNewInvestmentsConsumer(unittest.TestCase):
    def setUp(self) -> None:
        self.consumer = NewInvestmentsConsumer(
            dividends_client=MagicMock(),
            investments_client=MagicMock(),
            earnings_calculator=MagicMock()
        )

    def test_receive_edit_investment_with_no_dividends_affected_changes_should_not_process_anything(self):
        self.consumer.handle_applicable_cash_dividends = MagicMock()

        self.consumer.receive(
            subject="1111",
            new_investment=self.create_stock_investment(
                date=datetime(2022, 5, 1).date(),
                amount=Decimal(100),
                operation=OperationType.BUY
            ),
            old_investment=self.create_stock_investment(
                date=datetime(2022, 5, 1).date(),
                amount=Decimal(100),
                operation=OperationType.BUY
            )
        )
        self.consumer.handle_applicable_cash_dividends.assert_not_called()

    def test_receive_edit_investment_with_dividends_affected_changes_should_process_old_and_new_investment(self):
        self.consumer.handle_applicable_cash_dividends = MagicMock()

        self.consumer.receive(
            subject="1111",
            new_investment=self.create_stock_investment(
                date=datetime(2022, 5, 1).date(),
                amount=Decimal(100),
                operation=OperationType.BUY
            ),
            old_investment=self.create_stock_investment(
                date=datetime(2022, 5, 1).date(),
                amount=Decimal(99),
                operation=OperationType.BUY
            )
        )
        self.consumer.handle_applicable_cash_dividends.assert_called()
        self.assertTrue(self.consumer.handle_applicable_cash_dividends.call_count == 2)

    def test_receive_new_investment_should_process_new_investment(self):
        self.consumer.handle_applicable_cash_dividends = MagicMock()
        new_investment = self.create_stock_investment(
            date=datetime(2022, 5, 1).date(),
            amount=Decimal(100),
            operation=OperationType.BUY
        )
        self.consumer.receive(
            subject="1111",
            new_investment=new_investment,
            old_investment=None
        )
        self.consumer.handle_applicable_cash_dividends.assert_called_once()
        self.consumer.handle_applicable_cash_dividends.assert_called_once_with("1111", new_investment)

    def test_receive_delete_investment_should_process_old_investment(self):
        self.consumer.handle_applicable_cash_dividends = MagicMock()
        old_investment = self.create_stock_investment(
            date=datetime(2022, 5, 1).date(),
            amount=Decimal(100),
            operation=OperationType.BUY
        )
        self.consumer.receive(
            subject="1111",
            new_investment=None,
            old_investment=old_investment
        )
        self.consumer.handle_applicable_cash_dividends.assert_called_once()
        self.consumer.handle_applicable_cash_dividends.assert_called_once_with("1111", old_investment)

    def test_handle_applicable_cash_dividends_with_two_dividends(self):
        self.consumer.dividends_client.get_cash_dividends_for_ticker = MagicMock(return_value=[
            CashDividends(
                asset_issued="BRBIDICDAXX3",
                label="DIVIDENDO",
                last_date_prior=date(2021, 5, 7),
                id="DIVIDENDID",
                payment_date=date(2022, 5, 7),
                related_to="1 Semestre",
                approved_on=date(2021, 5, 5),
                isin_code="BRBIDICDAXX3",
                rate=Decimal(1.573833)
            ),
            CashDividends(
                asset_issued="BRBIDICDAXX3",
                label="DIVIDENDO",
                last_date_prior=date(2021, 5, 7),
                id="DIVIDENDID2",
                payment_date=date(2022, 5, 7),
                related_to="1 Semestre",
                approved_on=date(2021, 5, 5),
                isin_code="BRBIDICDAXX3",
                rate=Decimal(1.573833)
            )
        ])
        stock_dividend = StockDividend("BIDI11", "DIVIDENDO", Decimal("55.33"), "1", date(2022, 5, 5), "id")
        self.consumer.earnings_calculator.calculate_earnings_of_cash_dividend_for_subject = MagicMock(
            return_value=stock_dividend
        )
        self.consumer.handle_applicable_cash_dividends("1111", self.create_stock_investment(date=date(2020, 5, 6)))

        self.consumer.investments_client.batch_save.assert_called_once()
        args = self.consumer.investments_client.batch_save.call_args
        self.assertTrue(len(args[0][0]) == 2)

    def test_handle_applicable_cash_dividends_with_earnings_less_than_or_equal_zero_should_delete_investment(self):
        self.consumer.dividends_client.get_cash_dividends_for_ticker = MagicMock(return_value=[
            CashDividends(
                asset_issued="BRBIDICDAXX3",
                label="DIVIDENDO",
                last_date_prior=date(2021, 5, 7),
                id="DIVIDENDID",
                payment_date=date(2022, 5, 7),
                related_to="1 Semestre",
                approved_on=date(2021, 5, 5),
                isin_code="BRBIDICDAXX3",
                rate=Decimal(1.573833)
            ),
            CashDividends(
                asset_issued="BRBIDICDAXX3",
                label="DIVIDENDO",
                last_date_prior=date(2021, 5, 7),
                id="DIVIDENDID2",
                payment_date=date(2022, 5, 7),
                related_to="1 Semestre",
                approved_on=date(2021, 5, 5),
                isin_code="BRBIDICDAXX3",
                rate=Decimal(1.573833)
            )
        ])
        stock_dividend = StockDividend("BIDI11", "DIVIDENDO", Decimal("0.00"), "1", date(2022, 5, 5), "id")
        self.consumer.earnings_calculator.calculate_earnings_of_cash_dividend_for_subject = MagicMock(
            return_value=stock_dividend
        )
        self.consumer.handle_applicable_cash_dividends("1111", self.create_stock_investment(date=date(2020, 5, 6)))

        self.consumer.investments_client.batch_save.assert_not_called()
        self.consumer.investments_client.delete.assert_called()
        self.assertTrue(self.consumer.investments_client.delete.call_count == 2)


    @staticmethod
    def create_stock_investment(
            date: datetime.date,
            amount: Decimal = Decimal(100),
            operation: OperationType = OperationType.BUY,
            price: Decimal = Decimal(10.00),
            subject: str = "1111"
    ):
        return StockInvestment(
            subject=subject,
            operation=operation,
            date=date,
            amount=amount,
            id="12345",
            price=price,
            ticker="BIDI11",
            type=InvestmentType.STOCK,
            broker="TEST"
        )
