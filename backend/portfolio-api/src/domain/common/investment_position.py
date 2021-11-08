from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import datetime as dt
from decimal import Decimal

from domain.common.investments import OperationType, Investment, StockInvestment

DATE_FORMAT = "%Y%m%d"


@dataclass
class InvestmentPosition(ABC):
    date: dt.date
    sold_amount: Decimal = field(default_factory=lambda: Decimal(0))
    bought_amount: Decimal = field(default_factory=lambda: Decimal(0))
    bought_value: Decimal = field(default_factory=lambda: Decimal(0))
    sold_value: Decimal = field(default_factory=lambda: Decimal(0))

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = dt.datetime.strptime(self.date, DATE_FORMAT).date()

        self.sold_amount = Decimal(self.sold_amount).quantize(Decimal("0.01"))
        self.bought_amount = Decimal(self.bought_amount).quantize(Decimal("0.01"))
        self.bought_value = Decimal(self.bought_value).quantize(Decimal("0.01"))
        self.sold_value = Decimal(self.sold_value).quantize(Decimal("0.01"))

    @abstractmethod
    def add_investment(self, investment: Investment):
        """Adds the investment consolidating self attributes values"""

    def to_dict(self) -> dict:
        return {**self.__dict__, "date": self.date.strftime(DATE_FORMAT)}

    def is_empty(self) -> bool:
        return (
            not self.sold_amount
            and not self.bought_amount
            and not self.bought_value
            and not self.sold_value
        )


@dataclass
class StockPosition(InvestmentPosition):
    def __add__(self, other):
        sold_amount = self.sold_amount + other.sold_amount
        bought_amount = self.bought_amount + other.bought_amount
        bought_value = self.bought_value + other.bought_value
        sold_value = self.sold_value + other.sold_value

        return StockPosition(
            self.date, sold_amount, bought_amount, bought_value, sold_value
        )

    def add_investment(self, investment: StockInvestment):
        sold_amount = 0
        sold_value = 0
        bought_amount = 0
        bought_value = 0

        if investment.operation == OperationType.BUY:
            bought_amount = investment.amount
            bought_value = investment.amount * investment.price
        elif investment.operation == OperationType.SELL:
            sold_amount = investment.amount
            sold_value = investment.amount * investment.price
        elif investment.operation in [OperationType.SPLIT, OperationType.INCORP_ADD]:
            bought_amount = investment.amount
        elif investment.operation in [OperationType.GROUP, OperationType.INCORP_SUB]:
            sold_amount = investment.amount

        self.sold_amount += sold_amount
        self.sold_value += sold_value
        self.bought_amount += bought_amount
        self.bought_value += bought_value
