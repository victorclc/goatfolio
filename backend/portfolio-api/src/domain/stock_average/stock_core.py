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

    def save_asset_quantities(self, subject: str, asset_quantities: dict, date: datetime.date):
        asset = AssetQuantities(subject=subject, asset_quantities=asset_quantities, date=date)
        self.portfolio.save(asset)

    def get_stock_divergences(self, subject: str) -> List[dict]:
        asset = self.portfolio.find_asset_quantities(subject)
        if not asset:
            return []

        pendency = []
        portfolio = self.portfolio.find(subject)

        for ticker, expected_amount in asset.asset_quantities.items():
            summary = self.get_stock_summary_of_ticker(ticker, portfolio)
            if summary and summary.latest_position.amount == expected_amount or ticker.endswith("12"):
                continue

            logger.info(f"Ticker: {ticker} has divergence")
            transformation = self.transformation_client.get_ticker_transformation(
                subject, ticker,
                ((asset.date if asset.date else datetime.datetime.now()) - relativedelta(months=18)).date()
            )
            if not summary:
                if transformation.ticker in portfolio.stocks:
                    summary = portfolio.get_stock_summary(transformation.ticker)

            actual_amount = summary.latest_position.amount if summary else 0
            missing_amount = self.calculate_missing_amount(
                expected_amount,
                actual_amount,
                transformation.grouping_factor,
            )
            logger.info(f"missing_amount={missing_amount}")
            if missing_amount < 0:  # TODO review how to "fix" negative missing amount
                continue
            pendency.append(
                {
                    "ticker": ticker,
                    "expected_amount": expected_amount,
                    "actual_amount": actual_amount,
                    "missing_amount": missing_amount
                }
            )
        return pendency

    @staticmethod
    def calculate_missing_amount(
            expected_amount, actual_amount, grouping_factor
    ) -> Decimal:
        logger.info(
            f"Calculating missing amount. expected_amount={expected_amount}, actual_amount={actual_amount}, grouping_factor={grouping_factor}")
        if grouping_factor == 0:
            return expected_amount - actual_amount
        if grouping_factor < 1:
            divider = grouping_factor
        else:
            divider = grouping_factor + 1
        if actual_amount < 0:
            return (expected_amount / divider) - actual_amount
        return (expected_amount - actual_amount) / divider

    @staticmethod
    def get_stock_summary_of_ticker(ticker: str, portfolio: Portfolio) -> Optional[StockSummary]:
        if ticker in portfolio.stocks:
            return portfolio.get_stock_summary(ticker)
        for _, summary in portfolio.stocks.items():
            if ticker == summary.alias_ticker:
                return summary

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
