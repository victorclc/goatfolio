from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from goatcommons.decorators import enforce_types


@dataclass
class _InvestmentsBase:
    operation: str
    date: datetime
    type: str
    broker: str


@dataclass
class Investment(_InvestmentsBase):
    external_system: str = ""
    subject: str = ""
    id: str = ""
    costs: Decimal = Decimal(0)


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


@dataclass
class StockInvestment(Investment, _StockInvestmentsBase):
    alias_ticker: str = ''

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.utcfromtimestamp(float(self.date))
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount).quantize(Decimal('0.01'))
        if not isinstance(self.price, Decimal):
            self.price = Decimal(self.price).quantize(Decimal('0.01'))
        if not isinstance(self.costs, Decimal):
            self.costs = Decimal(self.costs).quantize(Decimal('0.01'))

    def to_dict(self):
        return {**self.__dict__, 'date': int(self.date.timestamp())}


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
