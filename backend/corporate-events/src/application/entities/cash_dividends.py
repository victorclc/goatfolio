from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

_DATE_FORMAT = "%Y%m%d"


@dataclass
class CashDividendsEntity:
    asset_issued: str
    payment_date: datetime.date
    rate: Decimal
    related_to: str
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str = ""
    id: str = None

    def __post_init__(self):
        if isinstance(self.payment_date, str):
            self.payment_date = datetime.strptime(self.payment_date, _DATE_FORMAT).date()
        if isinstance(self.approved_on, str):
            self.approved_on = datetime.strptime(self.approved_on, _DATE_FORMAT).date()
        if isinstance(self.last_date_prior, str):
            self.last_date_prior = datetime.strptime(self.last_date_prior, _DATE_FORMAT).date()
        if not isinstance(self.rate, Decimal):
            self.rate = Decimal(self.rate).quantize(Decimal("0.00000000001"))
        if not self.id:
            self.id = f"{self.payment_date.strftime(_DATE_FORMAT)}" \
                      f"#{self.label}#{self.approved_on.strftime(_DATE_FORMAT)}" \
                      f"#{self.last_date_prior.strftime(_DATE_FORMAT)}"

    def to_dict(self):
        return {
            **self.__dict__,
            "payment_date": self.payment_date.strftime(_DATE_FORMAT),
            "approved_on": self.approved_on.strftime(_DATE_FORMAT),
            "last_date_prior": self.last_date_prior.strftime(_DATE_FORMAT),
        }
