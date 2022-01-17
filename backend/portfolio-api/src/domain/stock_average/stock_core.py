import datetime
import datetime as dt
from decimal import Decimal
from typing import List, Optional
from uuid import uuid4

from dateutil.relativedelta import relativedelta

from domain.common.investment_consolidated import StockConsolidated
from domain.common.investment_summary import StockSummary
from domain.common.investments import OperationType, StockInvestment, InvestmentType
from domain.common.portfolio import Portfolio
from domain.performance.ticker_transformation import TickerTransformation
from domain.stock_average.assets_quantities import AssetQuantities
from ports.outbound.investment_repository import InvestmentRepository
from ports.outbound.portfolio_repository import PortfolioRepository
from ports.outbound.corporate_events_client import (
    CorporateEventsClient,
)

from aws_lambda_powertools import Logger

logger = Logger()


class StockCore:
    """Stock only specific endpoints"""

    def __init__(
        self,
        portfolio: PortfolioRepository,
        investments: InvestmentRepository,
        transformation_client: CorporateEventsClient,
    ):
        self.portfolio = portfolio
        self.investments = investments
        self.transformation_client = transformation_client

    def save_asset_quantities(self, subject: str, asset_quantities: dict):
        asset = AssetQuantities(subject=subject, asset_quantities=asset_quantities)
        self.portfolio.save(asset)

    def get_stock_divergences(self, subject: str) -> List[dict]:
        asset = self.portfolio.find_asset_quantities(subject)
        if not asset:
            return []
        portfolio = self.portfolio.find(subject)

        pendencies = []
        for ticker, expected_amount in asset.asset_quantities.items():
            if ticker.endswith("12"):
                continue
            transformation = self.transformation_client.get_ticker_transformation(
                subject, ticker, (datetime.datetime.now() - relativedelta(months=18)).date()
            )
            summary = self.get_stock_summary_of_ticker(
                ticker, portfolio, transformation
            )
            if not summary:
                pendencies.append(
                    {
                        "ticker": ticker,
                        "expected_amount": expected_amount,
                        "actual_amount": 0,
                        "missing_amount": self.calculate_missing_amount(
                            expected_amount,
                            0,
                            transformation.grouping_factor,
                        ),
                    }
                )
            else:
                if expected_amount != summary.latest_position.amount:
                    pendencies.append(
                        {
                            "ticker": ticker,
                            "expected_amount": expected_amount,
                            "actual_amount": summary.latest_position.amount,
                            "missing_amount": self.calculate_missing_amount(
                                expected_amount,
                                summary.latest_position.amount,
                                transformation.grouping_factor,
                            ),
                        }
                    )

        return pendencies

    @staticmethod
    def calculate_missing_amount(
        expected_amount, actual_amount, grouping_factor
    ) -> Decimal:
        if grouping_factor == 0:
            return expected_amount - actual_amount
        if actual_amount < 0:
            return (expected_amount / (grouping_factor + 1)) - actual_amount
        return (expected_amount - actual_amount) / (grouping_factor + 1)

    @staticmethod
    def get_stock_summary_of_ticker(
        ticker: str, portfolio: Portfolio, transformation: TickerTransformation
    ) -> Optional[StockSummary]:
        if ticker in portfolio.stocks:
            return portfolio.get_stock_summary(ticker)
        for _, summary in portfolio.stocks.items():
            if ticker == summary.alias_ticker:
                return summary

        if transformation.ticker in portfolio.stocks:
            return portfolio.get_stock_summary(transformation.ticker)

    def average_price_fix(
        self,
        subject: str,
        ticker: str,
        date: dt.date,
        broker: str,
        amount: Decimal,
        average_price: Decimal,
    ):
        # TODO VALIDAR PRECO NEGATIVO
        consolidated = self.get_stock_consolidated(subject, ticker)
        transformation = self.transformation_client.get_ticker_transformation(
            subject, ticker, date
        )

        price = self.calculate_new_investment_price(
            consolidated, amount, average_price, date, transformation
        )
        logger.info(f"Calculated price: {price}")

        investment = self.create_stock_investment(
            subject,
            date,
            broker,
            transformation.ticker,
            amount,
            price,
        )
        logger.info(f"Investment created: {investment}")
        self.investments.save(investment)

        return investment

    def get_stock_consolidated(self, subject, ticker) -> StockConsolidated:
        consolidations = self.portfolio.find_alias_ticker(
            subject, ticker, StockConsolidated
        )
        consolidations += self.portfolio.find_ticker(subject, ticker, StockConsolidated)
        if not consolidations:
            logger.info(f"No stock consolidations, creating one.")
            consolidations.append(StockConsolidated(subject=subject, ticker=ticker))
        return sum(consolidations[1:], consolidations[0])

    @staticmethod
    def create_stock_investment(subject, date, broker, ticker, amount, price):
        return StockInvestment(
            subject=subject,
            id=f"STOCK#{ticker}#FIX#{str(uuid4())}",
            date=date,
            type=InvestmentType.STOCK,
            operation=OperationType.BUY if amount > 0 else OperationType.SELL,
            broker=broker,
            ticker=ticker,
            amount=amount,
            price=price,
        )

    @staticmethod
    def create_dummy_buy_investment(amount: Decimal, date: datetime.date):
        return StockInvestment(
            subject="",
            id="",
            date=date,
            type=InvestmentType.STOCK,
            operation=OperationType.BUY,
            broker="",
            ticker="",
            amount=amount,
            price=Decimal(0),
        )

    def calculate_new_investment_price(
        self,
        consolidated: StockConsolidated,
        amount: Decimal,
        average_price: Decimal,
        date: datetime.date,
        transformation: TickerTransformation,
    ) -> Decimal:
        wrappers = consolidated.monthly_stock_position_wrapper_linked_list()
        if not wrappers.tail:
            return Decimal(average_price).quantize(Decimal("0.01"))

        consolidated.add_investment(
            self.create_dummy_buy_investment(
                amount
                + (
                    amount
                    + (wrappers.tail.amount if wrappers.tail.amount < 0 else Decimal(0))
                )
                * transformation.grouping_factor,
                date,
            )
        )
        wrappers = consolidated.monthly_stock_position_wrapper_linked_list()

        new_bought = wrappers.tail.bought_amount * average_price
        logger.info(f"{new_bought=}")

        return ((new_bought - wrappers.tail.bought_value) / amount).quantize(
            Decimal("0.01")
        )
