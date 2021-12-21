import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import List

DATE_FORMAT = "%d/%m/%Y"


@dataclass
class CompanyDetails:
    company_name: str
    trading_name: str
    ticker_code: str
    segment: str
    code_cvm: str
    url: str


@dataclass
class CompaniesUpdates:
    date: datetime.date
    companies: List[CompanyDetails]


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
    remarks: str = ""

    def __post_init__(self):
        if type(self.payment_date) == str:
            self.payment_date = datetime.datetime.strptime(self.payment_date, DATE_FORMAT).date()
        if type(self.approved_on) == str:
            self.approved_on = datetime.datetime.strptime(self.approved_on, DATE_FORMAT).date()
        if type(self.last_date_prior) == str:
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, DATE_FORMAT).date()
        if type(self.rate) == str:
            self.rate = Decimal(self.rate.replace(".", "").replace(",", "."))


@dataclass
class StockDividends:
    asset_issued: str
    factor: Decimal
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str

    def __post_init__(self):
        if type(self.approved_on) == str:
            self.approved_on = datetime.datetime.strptime(self.approved_on, DATE_FORMAT).date()
        if type(self.last_date_prior) == str:
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, DATE_FORMAT).date()
        if type(self.factor) == str:
            self.factor = Decimal(self.factor.replace(".", "").replace(",", "."))


@dataclass
class Subscriptions:
    asset_issued: str
    percentage: Decimal
    price_unit: Decimal
    trading_period: str
    subscription_date: datetime.date
    approved_on: datetime.date
    isin_code: str
    label: str
    last_date_prior: datetime.date
    remarks: str

    def __post_init__(self):
        if type(self.subscription_date) == str:
            self.subscription_date = datetime.datetime.strptime(self.subscription_date, DATE_FORMAT).date()
        if type(self.approved_on) == str:
            self.approved_on = datetime.datetime.strptime(self.approved_on, DATE_FORMAT).date()
        if type(self.last_date_prior) == str:
            self.last_date_prior = datetime.datetime.strptime(self.last_date_prior, DATE_FORMAT).date()
        if type(self.percentage) == str:
            self.percentage = Decimal(self.percentage.replace(".", "").replace(",", "."))
        if type(self.price_unit) == str:
            self.priceUnit = Decimal(self.price_unit.replace(".", "").replace(",", "."))


@dataclass
class CompanySupplement:
    cash_dividends: List[CashDividends]
    stock_dividends: List[StockDividends]
    subscriptions: List[Subscriptions]

    def __post_init__(self):
        self.cash_dividends = [CashDividends(**c) if type(c) == dict else c for c in self.cash_dividends]
        self.stock_dividends = [StockDividends(**c) if type(c) == dict else c for c in self.stock_dividends]
        self.subscriptions = [Subscriptions(**c) if type(c) == dict else c for c in self.subscriptions]
