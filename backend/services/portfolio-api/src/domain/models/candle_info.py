from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CandleInfo:
    open: Decimal
    close: Decimal
