from dataclasses import dataclass
from decimal import Decimal
from typing import List

from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent


@dataclass
class TickerTransformation:
    ticker: str
    grouping_factor: Decimal
    events: List[EarningsInAssetCorporateEvent]

    def to_dict(self):
        return {
            **self.__dict__,
            "events": [e.to_dict() for e in self.events]
        }
