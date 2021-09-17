import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

from domain.enums.operation_type import OperationType
from domain.models.investment import StockInvestment
from domain.models.portfolio import (
    Portfolio,
    StockConsolidated,
    StockPositionMonthlySummary,
    StockSummary,
    StockPosition,
)
from domain.portfolio_core import PortfolioCore


class TestPortfolioCore(unittest.TestCase):
    def setUp(self):
        self.core = PortfolioCore(repo=MagicMock())
        self.BUY_INVESTMENT = StockInvestment(
            Decimal(100),
            Decimal("15.50"),
            "BIDI11",
            OperationType.BUY,
            datetime(2021, 5, 12, tzinfo=timezone.utc),
            "STOCK",
            "Inter",
        )
        self.subject = "1111-2222-3333-4444"

    def test_one_new_investment_without_an_portfolio_should_persis_an_portfolio_and_an_stock_consolidated_objects(
        self,
    ):
        self.core.repo.find = MagicMock(
            return_value=Portfolio(self.subject, self.subject)
        )
        self.core.repo.find_ticker = MagicMock(return_value=[])
        self.core.repo.find_alias_ticker = MagicMock(return_value=[])

        self.core.consolidate_portfolio(self.subject, [self.BUY_INVESTMENT], [])

        portfolio = self.core.repo.save_portfolio.call_args_list[0].args[0]

        self.assertEqual(self.core.repo.save_portfolio.call_count, 1)
        self.assertEqual(self.core.repo.save_stock_consolidated.call_count, 1)

        self.assertEqual(
            portfolio.stocks[0].latest_position.amount, self.BUY_INVESTMENT.amount
        )
        self.assertEqual(
            portfolio.stocks[0].latest_position.invested_value,
            self.BUY_INVESTMENT.amount * self.BUY_INVESTMENT.price,
        )
        self.assertIsNone(portfolio.stocks[0].previous_position)
        self.assertEqual(portfolio.initial_date, self.BUY_INVESTMENT.date)

    def test_new_investment_with_an_existing_portfolio_and_existing_stock_consolidated_should_update_latest_and_previous_position_and_consolidate_history(
        self,
    ):
        position_summary = StockPositionMonthlySummary(
            date=datetime(2021, 4, 1, 0, 0, tzinfo=timezone.utc),
            amount=Decimal("100.00"),
            invested_value=Decimal("1550.00"),
            bought_value=Decimal("1550.00"),
            average_price=Decimal("15.50"),
        )
        stock_summary = StockSummary(ticker="BIDI11", latest_position=position_summary)
        portfolio = Portfolio(
            subject=self.subject,
            ticker=self.subject,
            initial_date=datetime(2021, 4, 12, 0, 0, tzinfo=timezone.utc),
            stocks=[stock_summary],
        )
        stock_consolidated = StockConsolidated(
            subject="1111-2222-3333-4444",
            ticker="BIDI11",
            alias_ticker="",
            initial_date=datetime(2021, 4, 12, 0, 0, tzinfo=timezone.utc),
            history=[
                StockPosition(
                    date=datetime(2021, 4, 12, 0, 0, tzinfo=timezone.utc),
                    bought_amount=Decimal("100.00"),
                    bought_value=Decimal("1550.00"),
                )
            ],
        )

        self.core.repo.find = MagicMock(return_value=portfolio)
        self.core.repo.find_ticker = MagicMock(return_value=[])
        self.core.repo.find_alias_ticker = MagicMock(return_value=[stock_consolidated])

        self.core.consolidate_portfolio(self.subject, [self.BUY_INVESTMENT], [])

        self.assertEqual(self.core.repo.save_portfolio.call_count, 1)
        self.assertEqual(self.core.repo.save_stock_consolidated.call_count, 1)
        self.assertIsNotNone(portfolio.stocks[0].previous_position)
        self.assertEqual(
            portfolio.stocks[0].latest_position.amount,
            portfolio.stocks[0].previous_position.amount + self.BUY_INVESTMENT.amount,
        )
        self.assertEqual(len(stock_consolidated.history), 2)

    # def test_bug(self):
    #     new_investments = [StockInvestment(amount=Decimal('16'), price=Decimal('5.55'), ticker='TIET4', operation='BUY',
    #                                        date=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), type='STOCK',
    #                                        broker='Inter', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='5379013d-1bde-489c-8d2f-7d43adb959e3', costs=Decimal('0'),
    #                                        alias_ticker='AESB3'),
    #                        StockInvestment(amount=Decimal('12'), price=Decimal('0'), ticker='TIET4',
    #                                        operation='INCORP_SUB',
    #                                        date=datetime(2021, 3, 27, 0, 0, tzinfo=timezone.utc), type='STOCK',
    #                                        broker='', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='TIET4INCORPORACAO2021012920210326BRAESBACNOR7', costs=Decimal('0'),
    #                                        alias_ticker='AESB3')]
    #     old_investments = [StockInvestment(amount=Decimal('16'), price=Decimal('5.55'), ticker='TIET4', operation='BUY',
    #                                        date=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
    #                                        type='STOCK', broker='Inter', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='5379013d-1bde-489c-8d2f-7d43adb959e3', costs=Decimal('0'),
    #                                        alias_ticker=''),
    #                        StockInvestment(amount=Decimal('0'), price=Decimal('0'), ticker='TIET4',
    #                                        operation='INCORP_SUB',
    #                                        date=datetime(2021, 3, 27, 0, 0, tzinfo=timezone.utc),
    #                                        type='STOCK', broker='', external_system='',
    #                                        subject='41e4a793-3ef5-4413-82e2-80919bce7c1a',
    #                                        id='TIET4INCORPORACAO2021012920210326BRAESBACNOR7', costs=Decimal('0'),
    #                                        alias_ticker='AESB3')]
    #
    #     self.core.consolidate_portfolio(self.subject, new_investments, old_investments)

    # TODO TEST ALL KINDS OF INVESTMENTS TYPE
