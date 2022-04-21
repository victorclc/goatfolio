from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

from domain.corporate_events.earnings_in_assets_event import EarningsInAssetCorporateEvent


@dataclass
class TickerTransformation:
    ticker: str
    grouping_factor: Decimal
    events: Optional[List[EarningsInAssetCorporateEvent]] = field(default_factory=list)
    previous_tickers: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.grouping_factor, Decimal):
            self.grouping_factor = Decimal(self.grouping_factor)
        self.events = [EarningsInAssetCorporateEvent(**e) for e in self.events]
