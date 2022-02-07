import datetime as dt
import unittest
from decimal import Decimal

from domain.common.investments import InvestmentType, OperationType, StockInvestment
from domain.common.investment_position import StockPosition


class TestStockPosition(unittest.TestCase):
    def test_add_buy_investment(self):
        buy_investment = self.create_buy_investment(
            amount=Decimal(100), price=Decimal(10)
        )
        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(buy_investment)

        self.assertEqual(position.bought_value, Decimal(1000))
        self.assertEqual(position.bought_amount, Decimal(100))
        self.assertEqual(position.sold_value, Decimal(0))
        self.assertEqual(position.sold_amount, Decimal(0))

    def test_add_sell_investment(self):
        sell_investment = self.create_sell_investment(
            amount=Decimal(100), price=Decimal(10)
        )
        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(sell_investment)

        self.assertEqual(position.bought_value, Decimal(0))
        self.assertEqual(position.bought_amount, Decimal(0))
        self.assertEqual(position.sold_value, Decimal(1000))
        self.assertEqual(position.sold_amount, Decimal(100))

    def test_add_split_investment(self):
        """Price should be unconsidered in split type investments"""
        split_investment = self.create_split_investment(
            amount=Decimal(100), price=Decimal(1111)
        )
        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(split_investment)

        self.assertEqual(position.bought_value, Decimal(0))
        self.assertEqual(position.bought_amount, Decimal(100))
        self.assertEqual(position.sold_value, Decimal(0))
        self.assertEqual(position.sold_amount, Decimal(0))

    def test_add_incorp_add_investment(self):
        """Price should be unconsidered in incorp_add type investments"""
        incorp_add_investment = self.create_incorp_add_investment(
            amount=Decimal(100), price=Decimal(10)
        )
        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(incorp_add_investment)

        self.assertEqual(position.bought_value, Decimal(0))
        self.assertEqual(position.bought_amount, Decimal(100))
        self.assertEqual(position.sold_value, Decimal(0))
        self.assertEqual(position.sold_amount, Decimal(0))

    def test_add_group_investment(self):
        """Price should be unconsidered in group type investments"""
        group_investment = self.create_group_investment(
            amount=Decimal(100), price=Decimal(1111)
        )
        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(group_investment)

        self.assertEqual(position.bought_value, Decimal(0))
        self.assertEqual(position.bought_amount, Decimal(-100))
        self.assertEqual(position.sold_value, Decimal(0))
        self.assertEqual(position.sold_amount, Decimal(0))

    def test_add_incorp_sub_investment(self):
        """Price should be unconsidered in incorp_sub type investments"""
        incorp_sub_investment = self.create_incorp_sub_investment(
            amount=Decimal(100), price=Decimal(10)
        )
        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(incorp_sub_investment)

        self.assertEqual(position.bought_value, Decimal(0))
        self.assertEqual(position.bought_amount, Decimal(-100))
        self.assertEqual(position.sold_value, Decimal(0))
        self.assertEqual(position.sold_amount, Decimal(0))

    def test_add_one_of_each_investment(self):
        buy_investment = self.create_buy_investment(
            amount=Decimal(1000), price=Decimal(150)
        )
        sell_investment = self.create_sell_investment(
            amount=Decimal(500), price=Decimal(200)
        )
        split_investment = self.create_split_investment(
            amount=Decimal(1000), price=Decimal(1111)
        )
        incorp_add_investment = self.create_incorp_add_investment(
            amount=Decimal(500), price=Decimal(10)
        )
        group_investment = self.create_group_investment(
            amount=Decimal(500), price=Decimal(1111)
        )
        incorp_sub_investment = self.create_incorp_sub_investment(
            amount=Decimal(500), price=Decimal(10)
        )

        position = StockPosition(dt.date(2021, 10, 1))
        position.add_investment(buy_investment)
        position.add_investment(sell_investment)
        position.add_investment(split_investment)
        position.add_investment(incorp_add_investment)
        position.add_investment(group_investment)
        position.add_investment(incorp_sub_investment)

        self.assertEqual(position.bought_value, Decimal(150000))
        self.assertEqual(position.bought_amount, Decimal(1500))
        self.assertEqual(position.sold_value, Decimal(100000))
        self.assertEqual(position.sold_amount, Decimal(500))

    def create_buy_investment(self, amount: Decimal, price: Decimal) -> StockInvestment:
        return self.create_investment(OperationType.BUY, amount, price)

    def create_sell_investment(
        self, amount: Decimal, price: Decimal
    ) -> StockInvestment:
        return self.create_investment(OperationType.SELL, amount, price)

    def create_split_investment(
        self, amount: Decimal, price: Decimal
    ) -> StockInvestment:
        return self.create_investment(OperationType.SPLIT, amount, price)

    def create_incorp_add_investment(
        self, amount: Decimal, price: Decimal
    ) -> StockInvestment:
        return self.create_investment(OperationType.INCORP_ADD, amount, price)

    def create_group_investment(
        self, amount: Decimal, price: Decimal
    ) -> StockInvestment:
        return self.create_investment(OperationType.GROUP, amount, price)

    def create_incorp_sub_investment(
        self, amount: Decimal, price: Decimal
    ) -> StockInvestment:
        return self.create_investment(OperationType.INCORP_SUB, amount, price)

    @staticmethod
    def create_investment(operation: OperationType, amount: Decimal, price: Decimal):
        return StockInvestment(
            subject="1111-2222-3333,4444",
            id="2222-2222-2222-2222",
            date=dt.date(2021, 10, 1),
            type=InvestmentType.STOCK,
            operation=operation,
            broker="Inter",
            ticker="BIDI11",
            amount=amount,
            price=price,
        )
