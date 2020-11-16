from dataclasses import dataclass
from decimal import Decimal

from goatcommons.constants import InvestmentsType, OperationType
from goatcommons.decorators import enforce_types


@enforce_types
@dataclass
class _InvestmentsBase:
    operation: str
    date: str
    type: str
    broker: str


@enforce_types
@dataclass
class Investment(_InvestmentsBase):
    external_system: str = ""
    subject: str = ""
    id: str = ""


@enforce_types
@dataclass
class _StockInvestmentsBase:
    amount: Decimal
    price: Decimal
    ticker: str


@enforce_types
@dataclass
class _CheckingAccountInvestmentBase:
    initial_date: str
    value: Decimal
    percent_over_cdi: Decimal


@enforce_types
@dataclass
class _PostFixedInvestmentBase:
    emitter: str
    paper: str
    indexer: str
    percent_over_cdi: Decimal
    expiration_date: str
    value: Decimal


@enforce_types
@dataclass
class _PreFixedInvestmentBase:
    emitter: str
    paper: str
    annual_tax: Decimal
    initial_date: str
    expiration_date: str
    value: Decimal


@enforce_types
@dataclass
class StockInvestment(Investment, _StockInvestmentsBase):
    pass


@enforce_types
@dataclass
class CheckingAccountInvestment(Investment, _CheckingAccountInvestmentBase):
    pass


@enforce_types
@dataclass
class PostFixedInvestment(Investment, _PostFixedInvestmentBase):
    pass


@enforce_types
@dataclass
class PreFixedInvestment(Investment, _PreFixedInvestmentBase):
    pass
