import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal

from application.investment_type import InvestmentType
from application.operation_type import OperationType

DATE_FORMAT = "%Y%m%d"


@dataclass
class Investment(ABC):
    subject: str
    id: str
    date: dt.date
    type: InvestmentType

    @abstractmethod
    def to_json(self):
        """Json representation of the data"""

    def __post_init__(self):
        if not isinstance(self.date, dt.date):
            self.date = dt.datetime.strptime(str(self.date), DATE_FORMAT).date()
        if isinstance(self.type, str):
            self.type = InvestmentType(self.type)


@dataclass
class StockInvestment(Investment):
    operation: OperationType
    ticker: str
    amount: Decimal
    price: Decimal
    broker: str
    costs: Decimal = field(default_factory=lambda: Decimal(0))
    alias_ticker: str = ""
    external_system: str = ""

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.operation, str):
            self.operation = OperationType.from_string(self.operation)
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount).quantize(Decimal("0.01"))
        if not isinstance(self.price, Decimal):
            self.price = Decimal(self.price).quantize(Decimal("0.01"))
        if not isinstance(self.costs, Decimal):
            self.costs = Decimal(self.costs).quantize(Decimal("0.01"))

    @property
    def current_ticker_name(self):
        return self.alias_ticker or self.ticker

    def to_json(self):
        return {
            **self.__dict__,
            "date": int(self.date.strftime(DATE_FORMAT)),
            "operation": self.operation.value,
            "type": self.type.value,
        }


@dataclass
class StockDividend(Investment):
    ticker: str
    label: str  # DIVIDENDO, RENDIMENTO, JCP
    amount: Decimal

    # alias_ticker: str = "" # sera q precisa?

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(self.amount).quantize(Decimal("0.01"))

    def to_json(self):
        return {
            **self.__dict__,
            "date": int(self.date.strftime(DATE_FORMAT)),
            "type": self.type.value,
        }
