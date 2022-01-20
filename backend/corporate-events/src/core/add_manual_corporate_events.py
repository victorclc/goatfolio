from datetime import datetime
from decimal import Decimal
from typing import Protocol

from aws_lambda_powertools import Logger

from application.enums.event_type import EventType
from application.exceptions.validation_errors import InvalidEmittedTickerError, InvalidLastDatePriorError, \
    InvalidGroupingFactorError
from application.models.earnings_in_assets_event import ManualEarningsInAssetCorporateEvents, \
    EarningsInAssetCorporateEvent
from application.models.manual_event import BonificacaoEvent, IncorporationEvent, GroupEvent, SplitEvent
from application.ports.ticker_info_client import TickerInfoClient
from application.converters import earnings_converter

logger = Logger()


class ManualEarningInAssetsRepository(Protocol):
    def save(self, event: ManualEarningsInAssetCorporateEvents):
        ...


class NewEventNotifier(Protocol):
    def notify(self, event: EarningsInAssetCorporateEvent):
        ...


def _validate_emitted_ticker(emitted_ticker: str, ticker_client: TickerInfoClient):
    if not ticker_client.is_ticker_valid(emitted_ticker):
        logger.info(f"Unknown emitted ticker: {emitted_ticker}")
        raise InvalidEmittedTickerError("Código do ativo emitido inválido.")


def _validate_last_date_prior(last_date_prior: datetime.date):
    if last_date_prior >= datetime.now().date():
        logger.info(f"Invalid last date prior: {last_date_prior}")
        raise InvalidLastDatePriorError("A data do evento não pode ser maior ou igual que a data atual.")


def _validate_grouping_factor(grouping_factor: Decimal):
    if grouping_factor < 0:
        raise InvalidGroupingFactorError("O fator de grupamento não pode ser menor que 0.")


def add_bonificacao_corporate_event(subject: str, bonificacao: BonificacaoEvent, repo: ManualEarningInAssetsRepository):
    pass


def add_incorporation_corporate_event(subject: str, incorporation: IncorporationEvent,
                                      repo: ManualEarningInAssetsRepository,
                                      ticker_client: TickerInfoClient,
                                      notifier: NewEventNotifier):
    _validate_last_date_prior(incorporation.last_date_prior)
    _validate_grouping_factor(incorporation.grouping_factor)
    if not ticker_client.is_ticker_valid(incorporation.emitted_ticker):
        raise InvalidEmittedTickerError("Código do ativo emitido inválido.")

    if incorporation.grouping_factor <= 1:
        grouping_factor = incorporation.grouping_factor
    else:
        # FIXME possivel bug se existir incorporacao com grouping factor 1.5
        grouping_factor = incorporation.grouping_factor - 1

    event = ManualEarningsInAssetCorporateEvents(subject=subject,
                                                 type=EventType.INCORPORATION,
                                                 ticker=incorporation.ticker,
                                                 deliberate_on=incorporation.last_date_prior,
                                                 last_date_prior=incorporation.last_date_prior,
                                                 grouping_factor=grouping_factor * 100,
                                                 emitted_ticker=incorporation.emitted_ticker)

    logger.info(f"Saving event: {event}")
    repo.save(event)
    notifier.notify(earnings_converter.manual_earning_to_earnings_in_assets_converter(event, ticker_client))


def add_group_corporate_event(subject: str, group: GroupEvent,
                              repo: ManualEarningInAssetsRepository,
                              client: TickerInfoClient,
                              notifier: NewEventNotifier):
    _validate_grouping_factor(group.grouping_factor)
    if group.grouping_factor >= 1:
        logger.info(f"Invalid grouping factor: {group.grouping_factor}")
        raise InvalidGroupingFactorError("O fator de grupamento não pode ser maior ou igual a 1.")
    _validate_last_date_prior(group.last_date_prior)

    event = ManualEarningsInAssetCorporateEvents(subject=subject,
                                                 type=EventType.GROUP,
                                                 ticker=group.ticker,
                                                 deliberate_on=group.last_date_prior,
                                                 last_date_prior=group.last_date_prior,
                                                 grouping_factor=group.grouping_factor,
                                                 emitted_ticker=group.ticker)
    logger.info(f"Saving event: {event}")
    repo.save(event)
    notifier.notify(earnings_converter.manual_earning_to_earnings_in_assets_converter(event, client))


def add_split_corporate_event(subject: str, split: SplitEvent,
                              repo: ManualEarningInAssetsRepository,
                              client: TickerInfoClient,
                              notifier: NewEventNotifier):
    _validate_grouping_factor(split.grouping_factor)
    if split.grouping_factor - 1 < 0:
        logger.info(f"Invalid grouping factor: {split.grouping_factor}")
        raise InvalidGroupingFactorError("O fator de grupamento não pode ser maior ou igual a 1.")
    _validate_last_date_prior(split.last_date_prior)

    event = ManualEarningsInAssetCorporateEvents(subject=subject,
                                                 type=EventType.SPLIT,
                                                 ticker=split.ticker,
                                                 deliberate_on=split.last_date_prior,
                                                 last_date_prior=split.last_date_prior,
                                                 grouping_factor=(split.grouping_factor - 1) * 100,
                                                 emitted_ticker=split.ticker)
    logger.info(f"Saving event: {event}")
    repo.save(event)
    notifier.notify(earnings_converter.manual_earning_to_earnings_in_assets_converter(event, client))


# TODO PENSAR MELHOR NESSE GROUPING FACTOR MALDIDO