from dataclasses import dataclass
from typing import Optional

from application.enums.ticker_type import TickerType


@dataclass
class TickerInfo:
    ticker: str
    bdi: str
    code: str
    company_name: str
    isin: str
    asset_type: Optional[TickerType] = None
