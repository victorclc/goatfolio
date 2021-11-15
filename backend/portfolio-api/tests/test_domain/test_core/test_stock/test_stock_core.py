import unittest
from decimal import Decimal
import datetime as dt


from unittest.mock import MagicMock

from dateutil.relativedelta import relativedelta

from domain.stock_average.stock_core import StockCore
from domain.common.investments import InvestmentType, OperationType, StockInvestment
from domain.common.investment_consolidated import StockConsolidated
from domain.performance.ticker_transformation import TickerTransformation


class TestStockCore(unittest.TestCase):
    def setUp(self) -> None:
        repo = MagicMock()
        transform_client = MagicMock()
        investment_repo = MagicMock()
        self.core = StockCore(repo, investment_repo, transform_client)

    def test_average_price_rounding_bug(self):
        consolidated = self.rounding_error_stock_consolidated()
        self.core.portfolio.find_alias_ticker = MagicMock(return_value=[])
        self.core.portfolio.find_ticker = MagicMock(return_value=[consolidated])
        self.core.transformation_client.get_ticker_transformation = MagicMock(
            return_value=TickerTransformation("BIDI11", Decimal(2))
        )
        print(consolidated.monthly_stock_position_wrapper_linked_list().tail.amount)

        investment = self.core.average_price_fix(
            subject="1111",
            ticker="BIDI11",
            date=dt.date(2020, 5, 9),
            broker="",
            amount=Decimal(226),
            average_price=Decimal(11.35),
        )

        self.assertEqual(investment.price, Decimal("16.95"))

    def test_average_price_fix(self):
        subject = "1111-2222-3333-4444-5555"
        ticker = "BIDI11"
        broker = "Inter"
        amount = Decimal(100)
        average_price = Decimal(75)
        date = dt.datetime.now().date() - relativedelta(months=18)

        consolidated = StockConsolidated(subject=subject, ticker=ticker)
        buy_investment = self.create_buy_investment(
            date=dt.date(2021, 9, 25), amount=Decimal(100), price=Decimal(100)
        )
        split_investment = self.create_split_investment(
            dt.date(2021, 9, 25), amount=Decimal(200)
        )
        consolidated.add_investment(buy_investment)
        consolidated.add_investment(split_investment)

        self.core.portfolio.find_alias_ticker = MagicMock(return_value=[])
        self.core.portfolio.find_ticker = MagicMock(return_value=[consolidated])
        self.core.transformation_client.get_ticker_transformation = MagicMock(
            return_value=TickerTransformation("TESTE4", Decimal(2))
        )

        investment = self.core.average_price_fix(
            subject, ticker, date, broker, amount, average_price
        )

        self.assertEqual(investment.ticker, "TESTE4")
        self.assertEqual(investment.price, Decimal(350))
        self.assertEqual(investment.amount, Decimal(100))

    def create_buy_investment(
        self, date: dt.date, amount: Decimal, price: Decimal, alias_ticker: str = ""
    ) -> StockInvestment:
        return self.create_investment(
            date, OperationType.BUY, amount, price, alias_ticker=alias_ticker
        )

    def create_split_investment(
        self, date: dt.date, amount: Decimal
    ) -> StockInvestment:
        return self.create_investment(
            date, OperationType.SPLIT, amount, Decimal(0), alias_ticker=""
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

    @staticmethod
    def rounding_error_stock_consolidated() -> StockConsolidated:
        return StockConsolidated(
            **{
                "subject": "41e4a793-3ef5-4413-82e2-80919bce7c1a",
                "alias_ticker": "",
                "history": [
                    {
                        "date": "20200921",
                        "sold_amount": 0,
                        "bought_amount": 25,
                        "sold_value": 0,
                        "bought_value": 1287.5,
                    },
                    {
                        "date": "20201109",
                        "sold_amount": 40,
                        "bought_amount": 0,
                        "sold_value": 2402.4,
                        "bought_value": 0,
                    },
                    {
                        "date": "20210305",
                        "sold_amount": 29,
                        "bought_amount": 0,
                        "sold_value": 4654.5,
                        "bought_value": 0,
                    },
                    {
                        "date": "20210412",
                        "sold_amount": 82,
                        "bought_amount": 0,
                        "sold_value": 15417.13,
                        "bought_value": 0,
                    },
                ],
                "ticker": "BIDI11",
                "initial_date": "20200509",
            }
        )
