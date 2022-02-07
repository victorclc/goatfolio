from datetime import datetime
from decimal import Decimal
from typing import List, Protocol, Optional

from aws_lambda_powertools import Logger
from dateutil.relativedelta import relativedelta

from application.models.assets_quantities import AssetQuantities
from domain.common.investment_summary import StockSummary
from domain.common.portfolio import Portfolio
from domain.performance.ticker_transformation import TickerTransformation

logger = Logger()


class AssetFinder(Protocol):
    def find_asset_quantities(self, subject: str) -> AssetQuantities:
        ...


class PortfolioFinder(Protocol):
    def find(self, subject: str) -> Portfolio:
        ...


class TransformationClient(Protocol):
    def get_ticker_transformation(self, subject: str, ticker: str, date_from: datetime.date) -> TickerTransformation:
        ...


def _get_ticker_transformation(subject: str, ticker: str, asset: AssetQuantities, client: TransformationClient):
    return client.get_ticker_transformation(
        subject, ticker,
        ((asset.date if asset.date else datetime.now()) - relativedelta(months=18)).date()
    )


def _calculate_missing_amount(
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


def _create_divergence(ticker: str, summary: StockSummary, expected_amount: Decimal,
                       transformation: TickerTransformation) -> Optional[dict]:
    actual_amount = summary.latest_position.amount if summary else 0
    missing_amount = _calculate_missing_amount(
        expected_amount,
        actual_amount,
        transformation.grouping_factor,
    )
    logger.info(f"missing_amount={missing_amount}")
    if missing_amount > 0:
        return {
            "ticker": ticker,
            "expected_amount": expected_amount,
            "actual_amount": actual_amount,
            "missing_amount": missing_amount
        }


def get_stock_divergences(subject: str, asset_finder: AssetFinder, portfolio_finder: PortfolioFinder,
                          transformation_client: TransformationClient) -> List[dict]:
    asset = asset_finder.find_asset_quantities(subject)
    if not asset:
        return []

    portfolio = portfolio_finder.find(subject)
    divergences = []

    for ticker, expected_amount in asset.asset_quantities.items():
        summary = portfolio.get_stock_summary(ticker)
        if summary and summary.latest_position.amount == expected_amount or ticker.endswith("12"):
            continue
        logger.info(f"Ticker: {ticker} has divergence")

        transformation = _get_ticker_transformation(subject, ticker, asset, transformation_client)
        if not summary:
            summary = portfolio.get_stock_summary(transformation.ticker)

        divergence = _create_divergence(ticker, summary, expected_amount, transformation)
        if divergence:
            divergences.append(divergence)
    return divergences
