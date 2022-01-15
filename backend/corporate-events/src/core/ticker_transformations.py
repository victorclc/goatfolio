from datetime import datetime
from decimal import Decimal
from typing import List, Protocol

from aws_lambda_powertools import Logger

from application.converters import earnings_converter
from application.enums.event_type import EventType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent, \
    ManualEarningsInAssetCorporateEvents
from application.models.ticker_transformation import TickerTransformation
from application.ports.corporate_events_repository import CorporateEventsRepository
from application.ports.ticker_info_client import TickerInfoClient

logger = Logger()


class ManualCorporateEventsRepository(Protocol):
    def find_by_ticker_from_date(self, subject: str, ticker: str, from_date: datetime.date) -> List[
        ManualEarningsInAssetCorporateEvents
    ]:
        ...

    def find_by_emitted_ticker_from_date_and_event_type(
            self, subject, event_type: EventType, emitted_ticker: str, from_date: datetime.date
    ) -> List[ManualEarningsInAssetCorporateEvents]:
        ...


def get_events_list(subject: str,
                    ticker: str,
                    isin: str,
                    date_from: datetime.date,
                    repo: CorporateEventsRepository,
                    manual_repo: ManualCorporateEventsRepository,
                    client: TickerInfoClient) -> List[EarningsInAssetCorporateEvent]:
    events_list = repo.find_by_isin_from_date(isin, date_from)

    if subject:
        manual_events = manual_repo.find_by_ticker_from_date(subject, ticker, date_from)
        logger.info(f"Found {len(manual_events)} manual events for subject {subject}")
        events_list += list(
            map(lambda e: earnings_converter.manual_earning_to_earnings_in_assets_converter(e, client),
                manual_events))
    return events_list


def get_emitted_ticker_events(subject: str,
                              ticker: str,
                              isin: str,
                              date_from: datetime.date,
                              client: TickerInfoClient,
                              repo: CorporateEventsRepository,
                              manual_repo: ManualCorporateEventsRepository) -> List[EarningsInAssetCorporateEvent]:
    events = repo.find_by_type_and_emitted_asset(
        EventType.INCORPORATION, isin, date_from
    )
    if subject:
        manual_events = manual_repo.find_by_emitted_ticker_from_date_and_event_type(subject, EventType.INCORPORATION,
                                                                                    ticker, date_from)
        logger.info(f"Found {len(manual_events)} manual emitted tickers events for subject {subject}")
        events += list(
            map(lambda e: earnings_converter.manual_earning_to_earnings_in_assets_converter(e, client),
                manual_events))
    return events


def transformations_in_ticker(current_ticker: str,
                              date_from: datetime.date,
                              ticker_info: TickerInfoClient,
                              repository: CorporateEventsRepository,
                              manual_events_repo: ManualCorporateEventsRepository,
                              subject: str):
    ticker = current_ticker
    isin = ticker_info.get_isin_code_from_ticker(current_ticker)
    events_list = get_events_list(subject, ticker, isin, date_from, repository, manual_events_repo, ticker_info)

    for emitted_event in get_emitted_ticker_events(subject, current_ticker, isin, date_from, ticker_info, repository,
                                                   manual_events_repo):
        ticker = ticker_info.get_ticker_from_isin_code(emitted_event.isin_code)
        events_list += get_events_list(subject, ticker, emitted_event.isin_code, date_from, repository,
                                       manual_events_repo, ticker_info)

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
