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
            transformation = self.transformation_client.get_ticker_transformation(
                ticker, (datetime.datetime.now() - relativedelta(months=18)).date()
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
                        "missing_amount": expected_amount
                        / transformation.grouping_factor,
                    }
                )
            else:
                if expected_amount != summary.latest_position.amount:
                    pendencies.append(
                        {
                            "ticker": ticker,
                            "expected_amount": expected_amount,
                            "actual_amount": summary.latest_position.amount,
                            "missing_amount": (
                                expected_amount - summary.latest_position.amount
                            )
                            / transformation.grouping_factor,
                        }
                    )

        return pendencies

    def get_stock_summary_of_ticker(
        self, ticker: str, portfolio: Portfolio, transformation: TickerTransformation
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
            ticker, date
        )
        i_amount = amount / transformation.grouping_factor
        price = self.calculate_new_investment_price(
            consolidated, i_amount, average_price
        )

        investment = self.create_stock_investment(
            subject,
            date,
            broker,
            transformation.ticker,
            i_amount,
            price,
        )
        self.investments.save(investment)

        return investment

    def get_stock_consolidated(self, subject, ticker):
        consolidations = self.portfolio.find_alias_ticker(
            subject, ticker, StockConsolidated
        )
        consolidations += self.portfolio.find_ticker(subject, ticker, StockConsolidated)
        if not consolidations:
            consolidations.append(StockConsolidated(subject=subject, ticker=ticker))
        return sum(consolidations[1:], consolidations[0])

    @staticmethod
    def create_stock_investment(subject, date, broker, ticker, amount, price):
        return StockInvestment(
            subject=subject,
            id=str(uuid4()),
            date=date,
            type=InvestmentType.STOCK,
            operation=OperationType.BUY,
            broker=broker,
            ticker=ticker,
            amount=amount,
            price=price,
        )

    @staticmethod
    def calculate_new_investment_price(
        consolidated: StockConsolidated, amount: Decimal, average_price: Decimal
    ) -> Decimal:
        wrappers = consolidated.monthly_stock_position_wrapper_linked_list()
        if not wrappers.tail:
            return Decimal(average_price).quantize(Decimal("0.01"))

        current_invested = wrappers.tail.current_invested_value
        new_invested = (wrappers.tail.amount + amount) * average_price

        return ((new_invested - current_invested) / amount).quantize(Decimal("0.01"))
