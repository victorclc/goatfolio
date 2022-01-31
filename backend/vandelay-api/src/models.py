from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import datetime as dt


class InvestmentType(Enum):
    STOCK = "STOCK"
    US_STOCK = "US_STOCK"
    FIXED_INCOME = "FIXED_INCOME"
    PRE_FIXED = "PRE_FIXED"
    POST_FIXED = "POST_FIXED"
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    CRYPTO = "CRYPTO"

    @classmethod
    def from_string(cls, _type: str):
        return cls(_type)


class OperationType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SPLIT = "SPLIT"
    GROUP = "GROUP"
    INCORP_ADD = "INCORP_ADD"
    INCORP_SUB = "INCORP_SUB"

    @classmethod
    def from_string(cls, _type: str):
        return cls(_type)


@dataclass
class StockInvestment:
    subject: str
    id: str
    date: dt.date
    type: InvestmentType
    operation: OperationType
    broker: str
    ticker: str
    amount: Decimal
    price: Decimal
    costs: Decimal = field(default_factory=lambda: Decimal(0))
    alias_ticker: str = ""
    external_system: str = ""

    def __post_init__(self):
        if not isinstance(self.date, dt.date):
            self.date = dt.datetime.strptime(str(self.date), "%Y%m%d").date()
        if isinstance(self.operation, str):
            self.operation = OperationType.from_string(self.operation)
        if isinstance(self.type, str):
            self.type = InvestmentType.from_string(self.type)
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount).quantize(Decimal("0.01"))
        if not isinstance(self.price, Decimal):
            self.price = Decimal(self.price).quantize(Decimal("0.01"))
        if not isinstance(self.costs, Decimal):
            self.costs = Decimal(self.costs).quantize(Decimal("0.01"))

    def to_dict(self):
        return {
            **self.__dict__,
            "date": int(self.date.strftime("%Y%m%d")),
            "operation": self.operation.value,
            "type": self.type.value,
        }

    @property
    def current_ticker_name(self):
        return self.alias_ticker or self.ticker


@dataclass
class CEIInboundRequest:
    tax_id: str
    password: str


@dataclass
class CEIOutboundRequest:
    subject: str
    datetime: int
    credentials: CEIInboundRequest


@dataclass
class CEIImportResult:
    subject: str
    datetime: int
    status: str
    payload: dict
    login_error: bool = False


@dataclass
class Import:
    subject: str
    datetime: int
    status: str
    username: str = None
    payload: str = None
    error_message: str = None


@dataclass
class InvestmentRequest:
    type: InvestmentType
    investment: dict

    def to_dict(self):
        return {**self.__dict__, "type": self.type.value}


@dataclass
class CEIInfo:
    subject: str
    asset_quantities: dict
    date: str
