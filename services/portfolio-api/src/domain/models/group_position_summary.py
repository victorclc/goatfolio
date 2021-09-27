from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Dict


class GroupPositionSummary(ABC):
    @property
    @abstractmethod
    def group_name(self) -> str:
        """Name of the group of investments. Eg.: STOCKS, REITS, CRYPTO"""

    @property
    @abstractmethod
    def opened_positions(self) -> List[Dict]:
        """Gets all active positions GroupItemInfo"""

    @property
    @abstractmethod
    def gross_value(self) -> Decimal:
        """Gets all active positions GroupItemInfo"""

    def to_dict(self) -> Dict:
        """Dict representation of the object"""
        return {
            "group_name": self.group_name,
            "gross_value": self.gross_value,
            "opened_positions": self.opened_positions,
        }

    def is_empty(self) -> bool:
        return self.opened_positions is None


@dataclass
class StockItemInfo:
    ticker: str
    quantity: Decimal
    average_price: Decimal
    last_price: Decimal


class StocksPositionSummary(GroupPositionSummary):
    def __init__(self):
        self._opened_positions = []
        self._gross_value = Decimal(0).quantize(Decimal("0.00"))

    @property
    def group_name(self) -> str:
        return "STOCKS"

    @property
    def gross_value(self) -> Decimal:
        return self._gross_value

    @property
    def opened_positions(self) -> List[Dict]:
        return [asdict(p) for p in self._opened_positions]

    def add_item_info(self, info: StockItemInfo):
        self._gross_value += info.quantity * info.last_price
        self._opened_positions.append(info)


class REITsPositionSummary(StocksPositionSummary):
    @property
    def group_name(self) -> str:
        return "REITS"


class BDRsPositionSummary(StocksPositionSummary):
    @property
    def group_name(self) -> str:
        return "BDRS"
