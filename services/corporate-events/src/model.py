from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from goatcommons.constants import InvestmentsType


@dataclass
class CompanyCorporateEventsData:
    company_name: str
    trading_name: str
    code: str
    segment: str
    code_cvm: str
    url: str


@dataclass
class EarningsInAssetCorporateEvent:
    type: str
    isin_code: str
    deliberate_on: datetime
    with_date: datetime
    grouping_factor: Decimal
    emitted_asset: str
    observations: str
    id: str = None

    def __post_init__(self):
        if type(self.with_date) is not datetime:
            self.with_date = datetime.strptime(self.with_date, '%Y%m%d')
        if type(self.deliberate_on) is not datetime:
            self.deliberate_on = datetime.strptime(self.deliberate_on, '%Y%m%d')
        if self.id is None:
            self.id = f"{self.isin_code}{self.type}{self.deliberate_on.strftime('%Y%m%d')}{self.emitted_asset}{self.with_date.strftime('%Y%m%d')}"

    def to_dict(self):
        return {**self.__dict__, 'with_date': self.with_date.strftime('%Y%m%d'),
                'deliberate_on': self.deliberate_on.strftime('%Y%m%d')}


@dataclass
class AsyncInvestmentAddRequest:
    subject: str
    type: InvestmentsType
    investment: dict
