from dataclasses import dataclass, field
from decimal import Decimal
import datetime as dt

from domain.enums.operation_type import OperationType


@dataclass
class StockInvestment:
    subject: str
    id: str
    operation: OperationType
    date: dt.date
    broker: str
    ticker: str
    amount: Decimal
    price: Decimal
    costs: Decimal = field(default_factory=lambda: Decimal(0))
    alias_ticker: str = ""
    external_system: str = ""

    type: str = "STOCK"

    def __post_init__(self):
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
        return {
            **self.__dict__,
            "date": int(self.date.strftime("%Y%m%d")),
            "operation": self.operation.value,
        }
