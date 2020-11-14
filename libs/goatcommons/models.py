from dataclasses import dataclass
from decimal import Decimal

from goatcommons.constants import InvestmentsType


@dataclass
class Investment:
    operation: str
    broker: str
    date: str
    id: str
    subject: str
    external_system: str
    type: str


@dataclass
class StockInvestment(Investment):
    type: str = InvestmentsType.STOCK
    subtype: str = None
    amount: Decimal = None
    price: Decimal = None
    costs: Decimal = 0
    ticker: str = None


@dataclass
class CheckingAccountInvestment(Investment):
    type: str = InvestmentsType.CHECKING_ACCOUNT
    initial_date: str = None
    value: Decimal = None
    percent_over_cdi: Decimal = None


@dataclass
class PostFixedInvestment(Investment):
    type: str = InvestmentsType.POST_FIXED
    emitter: str = None
    paper: str = None
    indexer: str = None
    percent_over_cdi: Decimal = None
    initial_date: str = None
    expiration_date: str = None
    value: Decimal = None


@dataclass
class PreFixedInvestment(Investment):
    type: str = InvestmentsType.PRE_FIXED
    emitter: str = None
    paper: str = None
    annual_tax: Decimal = None
    initial_date: str = None
    expiration_date: str = None
    value: Decimal = None
