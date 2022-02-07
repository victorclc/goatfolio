from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import uuid4

from aws_lambda_powertools import Logger

from domain.common.investment_consolidated import StockConsolidated
from domain.common.investments import StockInvestment, InvestmentType, OperationType
from domain.corporate_events.events_consolidation_strategies import handle_earning_in_assets_event
from domain.performance.ticker_transformation import TickerTransformation
from ports.outbound.investment_repository import InvestmentRepository
from ports.outbound.portfolio_repository import PortfolioRepository

logger = Logger()


class TransformationClient(Protocol):
    def get_ticker_transformation(self, subject: str, ticker: str, date_from: datetime.date) -> TickerTransformation:
        ...


def _get_stock_consolidated(subject, ticker, repository: PortfolioRepository) -> StockConsolidated:
    consolidations = repository.find_alias_ticker(
        subject, ticker, StockConsolidated
    )
    consolidations += repository.find_ticker(subject, ticker, StockConsolidated)
    if not consolidations:
        logger.info(f"No stock consolidations, creating one.")
        consolidations.append(StockConsolidated(subject=subject, ticker=ticker))
    return sum(consolidations[1:], consolidations[0])


def _create_stock_investment(subject, date, broker, ticker, amount, price):
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


def _create_dummy_buy_investment(amount: Decimal, date: datetime.date):
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


def average_price_quick_fix(subject: str, ticker: str, date: datetime.date, broker: str, amount: Decimal,
                            average_price: Decimal, investments_repo: InvestmentRepository,
                            transformation_client: TransformationClient):
    transformation = transformation_client.get_ticker_transformation(subject, ticker, date)
    investments = investments_repo.find_by_subject_and_ticker(subject, ticker)
    if transformation.ticker != ticker:
        investments += investments_repo.find_by_subject_and_ticker(subject, transformation.ticker)

    investments = list(filter(lambda i: i.operation in [OperationType.BUY, OperationType.SELL], investments))
    oldest_investment = min(investments, key=lambda i: i.date, default=datetime.max.date())
    if date > oldest_investment.date:
        transformation = transformation_client.get_ticker_transformation(subject, ticker, oldest_investment)

    investments.append(_create_dummy_buy_investment(amount, date))
    consolidated = StockConsolidated(subject)
    consolidated.add_investments(investments)

    for event in transformation.events:
        logger.info(f"Handling event {event} for {subject}")
        affected_investments = list(
            filter(
                lambda i, with_date=event.with_date: i.date <= with_date,
                investments,
            )
        )
        logger.info(f"len(affected_investment) is {len(affected_investments)}")

        new_investments = handle_earning_in_assets_event(subject, ticker, event, affected_investments)
        consolidated.add_investments(
            list(filter(lambda i: i.operation not in [OperationType.BUY, OperationType.SELL], new_investments)))

    wrappers = consolidated.monthly_stock_position_wrapper_linked_list()

    new_bought = wrappers.tail.bought_amount * average_price
    logger.info(f"{new_bought=}")

    price = ((new_bought - wrappers.tail.bought_value) / amount).quantize(
        Decimal("0.01")
    )
    logger.info(f"Calculated price: {price}")

    investment = _create_stock_investment(subject, date, broker, transformation.ticker, amount, price)
    logger.info(f"Investment created: {investment}")
    investments_repo.save(investment)

    return investment
