from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TickerTransformation:
    ticker: str
    grouping_factor: Decimal

    def __post_init__(self):
        if not isinstance(self.grouping_factor, Decimal):
            self.grouping_factor = Decimal(self.grouping_factor)
