import unittest
from decimal import Decimal
import datetime as dt

# VALIDAR SE TEVE SPLIT GROUP E COISAS DO TIPO NO MEIO DO CAMINHO
# DESCOBRI SE O TICKER TINHA UM NOME DIFERENTE 18 MESES ATRAS
from unittest.mock import MagicMock

from dateutil.relativedelta import relativedelta

from domain.core.stock.stock_core import StockCore
from domain.enums.investment_type import InvestmentType
from domain.enums.operation_type import OperationType
from domain.models.investment import StockInvestment
from domain.models.investment_consolidated import StockConsolidated


class TestStockCore(unittest.TestCase):
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

        repo = MagicMock()
        repo.find_alias_ticker = MagicMock(return_value=[consolidated])
        core = StockCore(repo=repo)
        investment = core.average_price_fix(
            subject, ticker, date, broker, amount, average_price
        )

        self.assertEqual(investment.price, Decimal(50))
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
