import datetime as dt
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

_DATE_FORMAT = "%Y%m%d"


class InvestmentType(Enum):
    STOCK = "STOCK"
    STOCK_DIVIDEND = "STOCK_DIVIDEND"
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
            self.date = dt.datetime.strptime(str(self.date), _DATE_FORMAT).date()
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
        if not self.type:
            self.type = InvestmentType.STOCK


@dataclass
class StockDividend:
    ticker: str
    label: str  # DIVIDENDO, RENDIMENTO, JCP
    amount: Decimal
    subject: str
    date: dt.date
    id: str
    type: InvestmentType = field(init=False)

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount).quantize(Decimal("0.01"))
        self.type = InvestmentType.STOCK_DIVIDEND

    def to_json(self):
        return {
            **self.__dict__,
            "date": int(self.date.strftime("%Y%m%d")),
            "type": self.type.value,
        }
