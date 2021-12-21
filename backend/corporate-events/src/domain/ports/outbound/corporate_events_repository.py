from typing import Protocol, List
import datetime

from domain.enums.event_type import EventType
from application.models.earnings_in_assets_event import EarningsInAssetCorporateEvent


class CorporateEventsRepository(Protocol):
    def find_by_isin_from_date(self, isin_code: str, date: datetime.date) -> List[EarningsInAssetCorporateEvent]:
        """Get all events of isin_code since date"""

    def find_by_type_and_date(
        self, event_type: EventType, date: datetime.date
    ) -> List[EarningsInAssetCorporateEvent]:
        """Get the events of event_type in date"""

    def batch_save(self, records: List[EarningsInAssetCorporateEvent]):
        """Saves a list of records"""

    def find_by_type_and_emitted_asset(
        self, event_type: EventType, emitted_isin: str, from_date: datetime.date
    ) -> List[EarningsInAssetCorporateEvent]:
        """Gets the event of event_type and emitted_isin from_date"""
