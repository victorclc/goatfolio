import datetime
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BonificacaoEvent:
    ticker: str
    base_value: Decimal
    last_date_prior: datetime.date

    def __post_init__(self):
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, "%Y%m%d").date()


@dataclass
class IncorporationEvent:
    ticker: str
    emitted_ticker: str
    grouping_factor: Decimal
    last_date_prior: datetime.date

    def __post_init__(self):
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, "%Y%m%d").date()


@dataclass
class GroupEvent:
    ticker: str
    grouping_factor: Decimal
    last_date_prior: datetime.date

    def __post_init__(self):
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, "%Y%m%d").date()


@dataclass
class SplitEvent:
    ticker: str
    grouping_factor: Decimal
    last_date_prior: datetime.date

    def __post_init__(self):
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, "%Y%m%d").date()
