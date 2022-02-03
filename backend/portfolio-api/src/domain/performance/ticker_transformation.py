from dataclasses import dataclass
from decimal import Decimal
from typing import List

from domain.corporate_events.earnings_in_assets_event import EarningsInAssetCorporateEvent


@dataclass
class TickerTransformation:
    ticker: str
    grouping_factor: Decimal
    events: List[EarningsInAssetCorporateEvent]

    def __post_init__(self):
        if not isinstance(self.grouping_factor, Decimal):
            self.grouping_factor = Decimal(self.grouping_factor)
        self.events = [EarningsInAssetCorporateEvent(**e) for e in self.events]
