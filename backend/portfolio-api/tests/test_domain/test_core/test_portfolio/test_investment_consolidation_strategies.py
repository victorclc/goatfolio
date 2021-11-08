import unittest
import datetime
from decimal import Decimal

from unittest.mock import MagicMock

from domain.common.investments import StockInvestment, InvestmentType, OperationType
from domain.investments.investment_consolidation_strategies import (
    StockConsolidationStrategy,
)


class TestStockConsolidationStrategy(unittest.TestCase):
    def setUp(self) -> None:
        repo = MagicMock()
        self.strategy = StockConsolidationStrategy(repo)

    def test_consolidate_new_stock_investment(self):
        new = StockInvestment(
            subject="1111-2222-3333-4444",
            id="STOCK#BIDI1113413531513531",
            date=datetime.date(2021, 10, 20),
            type=InvestmentType.STOCK,
            operation=OperationType.BUY,
            broker="Inter",
            ticker="BIDI11",
            amount=Decimal(100),
            price=Decimal(15.88)
        )
        self.strategy.repo.find_ticker = MagicMock(return_value=None)
        self.strategy.repo.find_alias_ticker = MagicMock(return_value=None)
        self.strategy.repo.save_all = MagicMock(return_value=None)
        self.strategy.consolidate("1111-2222-3333-4444", new, None)
