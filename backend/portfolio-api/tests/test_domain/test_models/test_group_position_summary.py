import unittest
from dataclasses import asdict
from decimal import Decimal

from domain.performance.group_position_summary import StocksPositionSummary, StockItemInfo


class TestStocksPositionSummary(unittest.TestCase):
    def test_add_item_info_gross_value(self):
        """Rather the StockItemInfo is being added correctly on the gross_value property"""
        info = StockItemInfo(
            ticker="BIDI11",
            quantity=Decimal(100),
            average_price=Decimal(1),
            last_price=Decimal(10),
            invested_value=Decimal(100),
        )
        summary = StocksPositionSummary()
        summary.add_item_info(info)

        self.assertEqual(summary.gross_value, Decimal(1000))

    def test_add_item_info_appended_to_opened_positions(self):
        """Rather the Info added is on the opened_positions"""
        info = StockItemInfo(
            ticker="BIDI11",
            quantity=Decimal(100),
            average_price=Decimal(1),
            last_price=Decimal(10),
            invested_value=Decimal(100),
        )
        summary = StocksPositionSummary()
        summary.add_item_info(info)

        self.assertIn(asdict(info), summary.opened_positions)

    def test_add_item_info_with_zero_quantity(self):
        """Rather the StockItemInfo is being ignored when quantity is 0 or less"""
        info = StockItemInfo(
            ticker="BIDI11",
            quantity=Decimal(0),
            average_price=Decimal(1),
            last_price=Decimal(10),
            invested_value=Decimal(100),
        )
        summary = StocksPositionSummary()
        summary.add_item_info(info)

        self.assertEqual(summary.gross_value, Decimal(0))

    def test_add_item_info_with_zero_quantity_not_appended_to_opened_positions(self):
        """Rather the Info added is on the opened_positions"""
        info = StockItemInfo(
            ticker="BIDI11",
            quantity=Decimal(100),
            average_price=Decimal(1),
            last_price=Decimal(10),
            invested_value=Decimal(100),
        )
        summary = StocksPositionSummary()
        summary.add_item_info(info)

        self.assertIn(asdict(info), summary.opened_positions)
