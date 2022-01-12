from typing import Protocol

from application.enums.event_type import EventType
from application.exceptions.invalid_emitted_ticker import InvalidEmittedTickerError
from application.exceptions.invalid_grouping_factor import InvalidGroupingFactorError
from application.models.earnings_in_assets_event import ManualEarningsInAssetCorporateEvents
from application.models.manual_event import BonificacaoEvent, IncorporationEvent, GroupEvent, SplitEvent
from application.ports.ticker_info_client import TickerInfoClient


class ManualEarningInAssetsRepository(Protocol):
    def save(self, event: ManualEarningsInAssetCorporateEvents):
        ...


def _validate_emitted_ticker(emitted_ticker: str, ticker_client: TickerInfoClient):
    if not ticker_client.is_ticker_valid(emitted_ticker):
        raise InvalidEmittedTickerError("Código do ativo emitido inválido.")


def add_bonificacao_corporate_event(subject: str, bonificacao: BonificacaoEvent, repo: ManualEarningInAssetsRepository):
    pass


def add_incorporation_corporate_event(subject: str, incorporation: IncorporationEvent,
                                      repo: ManualEarningInAssetsRepository,
                                      ticker_client: TickerInfoClient):
    event = ManualEarningsInAssetCorporateEvents(subject=subject,
                                                 type=EventType.INCORPORATION,
                                                 ticker=incorporation.ticker,
                                                 deliberate_on=incorporation.last_date_prior,
                                                 last_date_prior=incorporation.last_date_prior,
                                                 grouping_factor=incorporation.grouping_factor,
                                                 emitted_ticker=incorporation.emitted_ticker)

    if not ticker_client.is_ticker_valid(incorporation.emitted_ticker):
        raise InvalidEmittedTickerError("Código do ativo emitido inválido.")

    repo.save(event)


def add_group_corporate_event(subject: str, group: GroupEvent, repo: ManualEarningInAssetsRepository):
    if group.grouping_factor >= 1:
        raise InvalidGroupingFactorError("O fator de grupamento não pode ser maior ou igual a 1.")

    event = ManualEarningsInAssetCorporateEvents(subject=subject,
                                                 type=EventType.GROUP,
                                                 ticker=group.ticker,
                                                 deliberate_on=group.last_date_prior,
                                                 last_date_prior=group.last_date_prior,
                                                 grouping_factor=group.grouping_factor,
                                                 emitted_ticker=group.ticker)
    repo.save(event)


def add_split_corporate_event(subject: str, split: SplitEvent, repo: ManualEarningInAssetsRepository):
    event = ManualEarningsInAssetCorporateEvents(subject=subject,
                                                 type=EventType.SPLIT,
                                                 ticker=split.ticker,
                                                 deliberate_on=split.last_date_prior,
                                                 last_date_prior=split.last_date_prior,
                                                 grouping_factor=split.grouping_factor,
                                                 emitted_ticker=split.ticker)
    repo.save(event)
