from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TickerTransformation:
    ticker: str
    grouping_factor: Decimal
