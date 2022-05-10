import datetime
import unittest
from decimal import Decimal
from unittest.mock import MagicMock

from application.models.dividends import CashDividends
from application.models.invesments import InvestmentType, StockInvestment, OperationType
from core.calculators import CashDividendsEarningsCalculator


class TestCashDividendsEarningsHelper(unittest.TestCase):
    def setUp(self) -> None:
        self.dividend = CashDividends(
            asset_issued="BRBIDICDAXX3",
            label="DIVIDENDO",
            last_date_prior=datetime.date(2021, 5, 7),
            id="DIVIDENDID",
            payment_date=datetime.date(2022, 5, 7),
            related_to="1 Semestre",
            approved_on=datetime.date(2021, 5, 5),
            isin_code="BRBIDICDAXX3",
            rate=Decimal(1.573833)
        )
        self.helper = CashDividendsEarningsCalculator(
            events_client=MagicMock(),
            ticker_client=MagicMock(),
            investments_repository=MagicMock()
        )

    def test_get_applicable_investments_with_asset_issued_having_none_older_symbols_should_call_investments_repo_only_once(
            self):
        self.helper.events_client.get_all_previous_symbols.return_value = []
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = []

        self.helper.get_applicable_investments_for_cash_dividend(self.dividend)

        self.helper.ticker_client.get_ticker_from_isin_code.assert_called_once()
        self.helper.investments_repository.find_by_ticker_until_date.assert_called_once()

    def test_get_applicable_investments_with_asset_issued_having_multiple_older_symbols_should_call_investments_repo_only_once(
            self):
        self.helper.events_client.get_all_previous_symbols.return_value = ["SIMBOLO", "OUTROSIMBOLO"]
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = []

        self.helper.get_applicable_investments_for_cash_dividend(self.dividend)

        self.assertTrue(3 == self.helper.ticker_client.get_ticker_from_isin_code.call_count)
        self.assertTrue(3 == self.helper.investments_repository.find_by_ticker_until_date.call_count)

    def test_calculate_earnings_for_subject_with_applicable_investment_amount_sum_equals_zero(self):
        self.helper.events_client.get_all_previous_symbols.return_value = []
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = [
            self.create_stock_investment(
                date=self.dividend.last_date_prior,
                operation=OperationType.BUY,
                amount=Decimal(100)
            ),
            self.create_stock_investment(
                date=self.dividend.last_date_prior,
                operation=OperationType.SELL,
                amount=Decimal(100)
            ),
        ]
        ticker, earnings = self.helper.calculate_earnings_of_cash_dividend_for_subject("1111", self.dividend)

        self.assertTrue(earnings == Decimal(0))

    def test_calculate_earnings_for_subject_with_no_applicable_investment(self):
        self.helper.events_client.get_all_previous_symbols.return_value = []
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = []
        ticker, earnings = self.helper.calculate_earnings_of_cash_dividend_for_subject("1111", self.dividend)

        self.assertTrue(earnings == 0)

    def test_calculate_earnings_for_subject_with_applicable_investment_amount_greater_than_zero(self):
        self.helper.events_client.get_all_previous_symbols.return_value = []
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = [
            self.create_stock_investment(
                date=self.dividend.last_date_prior,
                operation=OperationType.BUY,
                amount=Decimal(100)
            ),
        ]
        ticker, earnings = self.helper.calculate_earnings_of_cash_dividend_for_subject("1111", self.dividend)

        self.assertTrue(earnings == Decimal("157.38"))

    def test_calculate_earnings_of_cash_dividends_for_all_users_with_no_applicable_investments(self):
        self.helper.events_client.get_all_previous_symbols.return_value = []
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = []
        earnings = self.helper.calculate_earnings_of_cash_dividend_for_all_users(self.dividend)

        self.assertTrue(len(earnings) == 0)

    def test_calculate_earnings_of_cash_dividends_for_all_users_with_multiple_applicable_investments(self):
        self.helper.events_client.get_all_previous_symbols.return_value = []
        self.helper.ticker_client.get_ticker_from_isin_code.return_value = "BIDI11"
        self.helper.investments_repository.find_by_ticker_until_date.return_value = [
            self.create_stock_investment(
                date=self.dividend.last_date_prior,
                operation=OperationType.BUY,
                amount=Decimal(100),
                subject="1"
            ),
            self.create_stock_investment(
                date=self.dividend.last_date_prior,
                operation=OperationType.BUY,
                amount=Decimal(100),
                subject="2"
            ),
            self.create_stock_investment(
                date=self.dividend.last_date_prior,
                operation=OperationType.SPLIT,
                amount=Decimal(100),
                subject="2"
            ),
        ]

        earnings = self.helper.calculate_earnings_of_cash_dividend_for_all_users(self.dividend)

        self.assertTrue(len(earnings) == 2)
        self.assertTrue(earnings[0]["subject"] == "1")
        self.assertTrue(earnings[0]["payed_amount"] == Decimal("157.38"))
        self.assertTrue(earnings[1]["subject"] == "2")
        self.assertTrue(earnings[1]["payed_amount"] == Decimal("314.77"))

    @staticmethod
    def create_stock_investment(
            date: datetime.date,
            amount: Decimal,
            operation: OperationType,
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
