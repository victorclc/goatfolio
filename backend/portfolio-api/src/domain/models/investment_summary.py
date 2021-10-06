from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from domain.models.investment_position_summary import (
    InvestmentPositionSummary,
    StockPositionSummary,
)


@dataclass
class InvestmentSummary(ABC):
    ticker: str
    latest_position: InvestmentPositionSummary
    previous_position: Optional[InvestmentPositionSummary] = None
    alias_ticker: str = field(default="")

    def to_dict(self) -> dict:
        ret = {**self.__dict__, "latest_position": self.latest_position.to_dict()}
        if self.previous_position:
            ret["previous_position"] = self.previous_position.to_dict()
        return ret

    @staticmethod
    def has_active_previous_position(self) -> bool:
        """Rather the previous position was active or not."""

    @abstractmethod
    def is_active(self) -> bool:
        """ "Rather the investment is active or not."""


@dataclass
class StockSummary(InvestmentSummary):
    def __post_init__(self):
        if isinstance(self.latest_position, dict):
            self.latest_position: StockPositionSummary = StockPositionSummary(
                **self.latest_position
            )
        if isinstance(self.previous_position, dict):
            self.previous_position: StockPositionSummary = StockPositionSummary(
                **self.previous_position
            )

    def is_active(self) -> bool:
        return self.latest_position.amount > 0

    def has_active_previous_position(self) -> bool:
        return self.previous_position and self.previous_position.amount > 0
