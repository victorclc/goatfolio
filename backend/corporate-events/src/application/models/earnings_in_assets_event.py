import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from application.models.companies_updates import StockDividends
from application.enums.event_type import EventType


@dataclass
class ManualEarningsInAssetCorporateEvents:
    subject: str
    type: EventType
    ticker: str
    deliberate_on: dt.date
    last_date_prior: dt.date
    grouping_factor: Decimal
    emitted_ticker: str
    id: Optional[str] = None

    def __post_init__(self):
        if type(self.grouping_factor) is not Decimal:
            self.grouping_factor = Decimal(self.grouping_factor).quantize(
                Decimal("0.00000000001")
            )
        if type(self.last_date_prior) is not dt.date:
            self.with_date = dt.datetime.strptime(str(self.last_date_prior), "%Y%m%d")
        if type(self.type) is str:
            self.type = EventType(self.type)
        if type(self.deliberate_on) is not dt.date:
            self.deliberate_on = dt.datetime.strptime(str(self.deliberate_on), "%Y%m%d")
        if not self.id:
            self.id = f"TICKER#{self.ticker}#{self.type}{self.deliberate_on.strftime('%Y%m%d')}{int(self.grouping_factor)}{self.emitted_ticker}{self.last_date_prior.strftime('%Y%m%d')}"

    def to_dict(self):
        return {
            **self.__dict__,
            "last_date_prior": self.last_date_prior.strftime("%Y%m%d"),
            "deliberate_on": self.deliberate_on.strftime("%Y%m%d"),
            "type": self.type.value,
        }


@dataclass
class EarningsInAssetCorporateEvent:
    type: EventType
    isin_code: str
    deliberate_on: dt.date
    with_date: dt.date
    grouping_factor: Decimal
    emitted_asset: str
    observations: str
    id: Optional[str] = None
    emitted_ticker: Optional[str] = None

    @property
    def factor(self):
        if self.type == EventType.GROUP:
            return Decimal(self.grouping_factor)
        return Decimal(self.grouping_factor / 100)

    @classmethod
    def from_stock_dividends(cls, sd: StockDividends):
        return cls(type=EventType(sd.label),
                   isin_code=sd.isin_code,
                   deliberate_on=sd.approved_on,
                   with_date=sd.last_date_prior,
                   grouping_factor=sd.factor,
                   emitted_asset=sd.asset_issued,
                   observations=sd.remarks)

    def __post_init__(self):
        if type(self.type) is str:
            self.type = EventType(self.type)
        if type(self.with_date) is not dt.date:
            self.with_date = dt.datetime.strptime(str(self.with_date), "%Y%m%d")
        if type(self.deliberate_on) is not dt.date:
            self.deliberate_on = dt.datetime.strptime(str(self.deliberate_on), "%Y%m%d")
        if self.id is None:
            self.id = f"{self.isin_code}{self.type}{self.deliberate_on.strftime('%Y%m%d')}{int(self.grouping_factor)}{self.emitted_asset}{self.with_date.strftime('%Y%m%d')}"
        if type(self.grouping_factor) is not Decimal:
            self.grouping_factor = Decimal(self.grouping_factor).quantize(
                Decimal("0.00000000001")
            )
        elif type(self.grouping_factor) is Decimal:
            self.grouping_factor = self.grouping_factor.quantize(Decimal("0.00000000001"))
        if type(self.observations) is not str:
            self.observations = ""
        if type(self.emitted_asset) is not str:
            self.emitted_asset = ""

    def to_dict(self):
        return {
            **self.__dict__,
            "with_date": self.with_date.strftime("%Y%m%d"),
            "deliberate_on": self.deliberate_on.strftime("%Y%m%d"),
            "type": self.type.value,
        }
