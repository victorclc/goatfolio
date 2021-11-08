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
        consolidated.add_investment(buy_investment)

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
