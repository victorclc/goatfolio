from decimal import Decimal
import math
from typing import List

from dateutil.relativedelta import relativedelta

from domain.enums.operation_type import OperationType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from domain.models.stock_investment import StockInvestment
from domain.ports.outbound.ticker_info_client import TickerInfoClient


def handle_split_event_strategy(
    subject: str,
    ticker: str,
    event: EarningsInAssetCorporateEvent,
    investments: List[StockInvestment],
    ticker_info: TickerInfoClient,
) -> List[StockInvestment]:
    amount = affected_investments_amount(investments)
    factor = Decimal(event.grouping_factor / 100)
    _id = create_id_from_corp_event(ticker, event)
    split_investment = StockInvestment(
        amount=amount * factor,
        price=Decimal(0),
        ticker=ticker,
        operation=OperationType.SPLIT,
        date=event.with_date + relativedelta(days=1),
        broker="",
        subject=subject,
        id=_id,
    )
    return [split_investment]


def handle_group_event_strategy(
    subject: str,
    ticker: str,
    event: EarningsInAssetCorporateEvent,
    investments: List[StockInvestment],
    ticker_info: TickerInfoClient,
) -> List[StockInvestment]:
    amount = affected_investments_amount(investments)
    _id = create_id_from_corp_event(ticker, event)
    factor = event.grouping_factor
    group_investment = StockInvestment(
        amount=amount
        - Decimal(math.ceil((amount * Decimal(factor)).quantize(Decimal("0.01")))),
        price=Decimal(0),
        ticker=ticker,
        operation=OperationType.GROUP,
        date=event.with_date + relativedelta(days=1),
        broker="",
        subject=subject,
        id=_id,
    )
    return [group_investment]


def handle_incorporation_event_strategy(
    subject: str,
    ticker: str,
    event: EarningsInAssetCorporateEvent,
    investments: List[StockInvestment],
    ticker_info: TickerInfoClient,
):
    new_ticker = ticker_info.get_ticker_from_isin_code(event.emitted_asset)
    amount = affected_investments_amount(investments)
    factor = Decimal(event.grouping_factor / 100)
    _id = create_id_from_corp_event(ticker, event)

    if factor > 1:
        incorp_investment = StockInvestment(
            amount=amount * factor,
            price=Decimal(0),
            ticker=ticker,
            operation=OperationType.INCORP_ADD,
            alias_ticker=new_ticker,
            date=event.with_date + relativedelta(days=1),
            broker="",
            subject=subject,
            id=_id,
        )
    elif factor < 1:
        incorp_investment = StockInvestment(
            amount=amount
            - Decimal(math.ceil((amount * Decimal(factor)).quantize(Decimal("0.01")))),
            price=Decimal(0),
            ticker=ticker,
            operation=OperationType.INCORP_SUB,
            alias_ticker=new_ticker,
            date=event.with_date + relativedelta(days=1),
            broker="",
            subject=subject,
            id=_id,
        )
    else:
        incorp_investment = StockInvestment(
            amount=Decimal(0),
            price=Decimal(0),
            alias_ticker=new_ticker,
            ticker=ticker,
            operation=OperationType.INCORP_ADD,
            date=event.with_date + relativedelta(days=1),
            broker="",
            subject=subject,
            id=_id,
        )

    for investment in investments:
        investment.alias_ticker = new_ticker
    affected_investments = investments.copy().append(incorp_investment)

    return affected_investments


def create_id_from_corp_event(ticker, event):
    return f"{ticker}{event.type}{event.deliberate_on.strftime('%Y%m%d')}{event.with_date.strftime('%Y%m%d')}{event.emitted_asset}"


def affected_investments_amount(affected_investments):
    amount = Decimal(0)
    for inv in affected_investments:
        if inv.operation in [
            OperationType.BUY,
            OperationType.SPLIT,
            OperationType.INCORP_ADD,
        ]:
            amount = amount + inv.amount
        else:
            amount = amount - inv.amount
    return amount
