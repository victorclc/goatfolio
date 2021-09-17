from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from domain.enums.investment_type import InvestmentType
from domain.enums.operation_type import OperationType


@dataclass
class _InvestmentsBase:
    operation: OperationType
    date: datetime
    type: InvestmentType
    broker: str

    def __post_init__(self):
        if isinstance(self.operation, str):
            self.operation = OperationType.from_string(self.operation)
        if isinstance(self.type, str):
            self.type = InvestmentType.from_string(self.type)


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


@dataclass
class _CheckingAccountInvestmentBase:
    initial_date: str
    value: Decimal
    percent_over_cdi: Decimal


@dataclass
class _PostFixedInvestmentBase:
    emitter: str
    paper: str
    indexer: str
    percent_over_cdi: Decimal
    expiration_date: str
    value: Decimal


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
    alias_ticker: str = ""

    def __post_init__(self):
        if not isinstance(self.date, datetime):
            self.date = datetime.fromtimestamp(float(self.date), tz=timezone.utc)  # type: ignore
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount).quantize(Decimal("0.01"))
        if not isinstance(self.price, Decimal):
            self.price = Decimal(self.price).quantize(Decimal("0.01"))
        if not isinstance(self.costs, Decimal):
            self.costs = Decimal(self.costs).quantize(Decimal("0.01"))

    @property
    def current_ticker_name(self):
        return self.alias_ticker or self.ticker

    def to_dict(self):
        return {**self.__dict__, "date": int(self.date.timestamp())}


@dataclass
class CheckingAccountInvestment(Investment, _CheckingAccountInvestmentBase):
    pass


@dataclass
class PostFixedInvestment(Investment, _PostFixedInvestmentBase):
    pass


@dataclass
class PreFixedInvestment(Investment, _PreFixedInvestmentBase):
    pass
