import unittest
import datetime as dt
from decimal import Decimal

from domain.enums.investment_type import InvestmentType
from domain.enums.operation_type import OperationType
from domain.models.investment import StockInvestment
from domain.models.investment_consolidated import StockConsolidated


class TestStockConsolidated(unittest.TestCase):
    @staticmethod
    def create_stock_consolidated():
        return StockConsolidated(subject="1111-2222-3333-4444", ticker="BIDI11")

    def test_add_investments_should_pick_the_min_date_as_initial_date(self):
        buy_investment1 = self.create_buy_investment(
            date=dt.date(2021, 9, 25), amount=Decimal(100), price=Decimal(50)
        )
        buy_investment2 = self.create_buy_investment(
            date=dt.date(2021, 9, 24), amount=Decimal(100), price=Decimal(50)
        )

        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment1)
        consolidated.add_investment(buy_investment2)

        self.assertEqual(consolidated.initial_date, dt.date(2021, 9, 24))

    def test_add_investment_with_alias_ticker_should_update_consolidate_alias_ticker(
        self,
    ):
        buy_investment = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
            alias_ticker="AAAA11",
        )

        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment)

        self.assertEqual(consolidated.alias_ticker, "AAAA11")

    def test_add_investment_without_alias_ticker_should_not_update_consolidate_alias_ticker(
        self,
    ):
        buy_investment = self.create_buy_investment(
            date=dt.date(2021, 9, 25), amount=Decimal(100), price=Decimal(50)
        )

        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment)

        self.assertFalse(consolidated.alias_ticker)

    def test_add_and_remove_investment_should_remove_position_from_history(
        self,
    ):
        buy_investment = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
            alias_ticker="AAAA11",
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment)
        buy_investment.amount *= -1
        consolidated.add_investment(buy_investment)

        self.assertFalse(consolidated.history)

    def test_add_investments_with_no_matching_dates_should_add_position_to_history_for_each_one(
        self,
    ):
        buy_investment1 = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment2 = self.create_buy_investment(
            date=dt.date(2021, 9, 24),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment3 = self.create_buy_investment(
            date=dt.date(2021, 8, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment1)
        consolidated.add_investment(buy_investment2)
        consolidated.add_investment(buy_investment3)

        self.assertEqual(len(consolidated.history), 3)

    def test_add_investments_with_matching_dates_should_add_only_one_position_to_history(
        self,
    ):
        buy_investment1 = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment2 = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment3 = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment1)
        consolidated.add_investment(buy_investment2)
        consolidated.add_investment(buy_investment3)

        self.assertEqual(len(consolidated.history), 1)

    def test_export_investment_summary_with_only_one_position_in_history(self):
        """ "Should return a StockSummary with the previous_position None"""
        buy_investment = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment)

        summary = consolidated.export_investment_summary()

        self.assertIsNone(summary.previous_position)
        self.assertEqual(summary.latest_position.amount, 100)
        self.assertEqual(summary.latest_position.date, dt.date(2021, 9, 1))
        self.assertEqual(summary.latest_position.bought_value, 5000)
        self.assertEqual(summary.latest_position.invested_value, 5000)

    def test_export_investment_summary_with_multiple_position_in_the_same_year_month_in_history(
        self,
    ):
        """ "Should return a StockSummary with the previous_position None"""
        buy_investment1 = self.create_buy_investment(
            date=dt.date(2021, 9, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment2 = self.create_buy_investment(
            date=dt.date(2021, 9, 24),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment3 = self.create_buy_investment(
            date=dt.date(2021, 9, 23),
            amount=Decimal(100),
            price=Decimal(50),
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment1)
        consolidated.add_investment(buy_investment2)
        consolidated.add_investment(buy_investment3)

        summary = consolidated.export_investment_summary()

        self.assertIsNone(summary.previous_position)
        self.assertEqual(summary.latest_position.amount, 300)
        self.assertEqual(summary.latest_position.date, dt.date(2021, 9, 1))
        self.assertEqual(summary.latest_position.bought_value, 15000)
        self.assertEqual(summary.latest_position.invested_value, 15000)

    def test_export_investment_summary_with_multiple_position_different_months_in_history(
        self,
    ):
        """previous_position should correspond the investments of the previous month"""
        buy_investment1 = self.create_buy_investment(
            date=dt.date(2021, 7, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment2 = self.create_buy_investment(
            date=dt.date(2021, 8, 24),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment3 = self.create_buy_investment(
            date=dt.date(2021, 9, 23),
            amount=Decimal(100),
            price=Decimal(50),
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment1)
        consolidated.add_investment(buy_investment2)
        consolidated.add_investment(buy_investment3)

        summary = consolidated.export_investment_summary()

        self.assertIsNotNone(summary.previous_position)
        self.assertEqual(summary.latest_position.amount, Decimal(300))
        self.assertEqual(summary.latest_position.date, dt.date(2021, 9, 1))
        self.assertEqual(summary.latest_position.bought_value, 5000)
        self.assertEqual(summary.latest_position.invested_value, 15000)
        self.assertEqual(summary.previous_position.amount, Decimal(200))
        self.assertEqual(summary.previous_position.date, dt.date(2021, 8, 1))
        self.assertEqual(summary.previous_position.bought_value, Decimal(5000))
        self.assertEqual(summary.previous_position.invested_value, Decimal(10000))

    def test_export_investment_summary_with_multiple_position_different_months_and_sell_investment_in_the_middle(
        self,
    ):
        """previous_position should correspond the investments of the previous month"""
        buy_investment1 = self.create_buy_investment(
            date=dt.date(2021, 7, 25),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment2 = self.create_sell_investment(
            date=dt.date(2021, 8, 24),
            amount=Decimal(100),
            price=Decimal(50),
        )
        buy_investment3 = self.create_buy_investment(
            date=dt.date(2021, 9, 23),
            amount=Decimal(100),
            price=Decimal(50),
        )
        consolidated = self.create_stock_consolidated()
        consolidated.add_investment(buy_investment1)
        consolidated.add_investment(buy_investment2)
        consolidated.add_investment(buy_investment3)

        summary = consolidated.export_investment_summary()

        self.assertIsNotNone(summary.previous_position)
        self.assertEqual(summary.latest_position.amount, Decimal(100))
        self.assertEqual(summary.latest_position.date, dt.date(2021, 9, 1))
        self.assertEqual(summary.latest_position.bought_value, Decimal(5000))
        self.assertEqual(summary.latest_position.invested_value, Decimal(5000))
        self.assertEqual(summary.previous_position.amount, Decimal(0))
        self.assertEqual(summary.previous_position.date, dt.date(2021, 8, 1))
        self.assertEqual(summary.previous_position.bought_value, Decimal(0))
        self.assertEqual(summary.previous_position.invested_value, Decimal(0))

    def create_buy_investment(
        self, date: dt.date, amount: Decimal, price: Decimal, alias_ticker: str = ""
    ) -> StockInvestment:
        return self.create_investment(
            date, OperationType.BUY, amount, price, alias_ticker=alias_ticker
        )

    def create_sell_investment(
        self, date: dt.date, amount: Decimal, price: Decimal, alias_ticker: str = ""
    ) -> StockInvestment:
        return self.create_investment(
            date, OperationType.SELL, amount, price, alias_ticker=alias_ticker
        )

    @staticmethod
    def create_investment(
        date: dt.date,
        operation: OperationType,
        amount: Decimal,
        price: Decimal,
        alias_ticker: str,
    ):
        return StockInvestment(
            subject="1111-2222-3333,4444",
            id="2222-2222-2222-2222",
            date=date,
            type=InvestmentType.STOCK,
            operation=operation,
            broker="Inter",
            ticker="BIDI11",
            amount=amount,
            price=price,
            alias_ticker=alias_ticker,
        )
