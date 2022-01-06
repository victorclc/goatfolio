import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BonificacaoEvent:
    ticker: str
    base_value: Decimal
    last_date_prior: datetime.date


@dataclass
class IncorporationEvent:
    ticker: str
    emitted_ticker: str
    grouping_factor: Decimal
    last_date_prior: datetime.date


@dataclass
class GroupEvent:
    ticker: str
    grouping_factor: Decimal
    last_date_prior: datetime.date


@dataclass
class SplitEvent:
    ticker: str
    grouping_factor: Decimal
    last_date_prior: datetime.date

