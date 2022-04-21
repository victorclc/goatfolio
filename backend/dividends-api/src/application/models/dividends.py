from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

_DATE_FORMAT = "%Y%m%d"


@dataclass
class CashDividends:
    asset_issued: str
    payment_date: datetime.date
    rate: Decimal
    related_to: str
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    id: str
    remarks: str = ""

    def __post_init__(self):
        if isinstance(self.payment_date, str):
            self.payment_date = datetime.strptime(self.payment_date, _DATE_FORMAT).date()
        if isinstance(self.approved_on, str):
            self.approved_on = datetime.strptime(self.approved_on, _DATE_FORMAT).date()
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.strptime(self.last_date_prior, _DATE_FORMAT).date()
        if not isinstance(self.rate, Decimal):
            self.rate = Decimal(self.rate).quantize(Decimal("0.00000000001"))
