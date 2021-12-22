from datetime import datetime
from decimal import Decimal
from typing import List

from application.enums.event_type import EventType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent
from application.models.ticker_transformation import TickerTransformation
from application.ports.corporate_events_repository import CorporateEventsRepository
from application.ports.ticker_info_client import TickerInfoClient


def transformations_in_ticker(current_ticker: str, date_from: datetime.date,
                              ticker_info: TickerInfoClient, repository: CorporateEventsRepository):
    ticker = current_ticker
    isin = ticker_info.get_isin_code_from_ticker(ticker)
    events_list: List[
        EarningsInAssetCorporateEvent
    ] = repository.find_by_isin_from_date(isin, date_from)

    tmp = repository.find_by_type_and_emitted_asset(
        EventType.INCORPORATION, isin, date_from
    )
    if tmp:
        previous_isin = tmp[0].isin_code
        ticker = ticker_info.get_ticker_from_isin_code(previous_isin)
        events_list += repository.find_by_isin_from_date(previous_isin, date_from)

    events_list = list(
        filter(
            lambda e: e.type != EventType.BONIFICACAO,
            # TODO: adicionar compatibilidade com eventtype bonificacao no resto do sistema
            filter(
                lambda e: not (e.type == EventType.INCORPORATION and e.factor == 1),
                events_list,
            )
        )
    )

    factor = Decimal(0)
    if events_list:
        factor = Decimal(1)
        for event in events_list:
            factor *= event.factor

    return TickerTransformation(ticker, factor)
