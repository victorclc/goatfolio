from typing import Protocol, List
import datetime

from domain.core.enums.event_type import EventType


class CorporateEventsRepository(Protocol):
    def find_by_isin_from_date(self, isin_code: str, date: datetime.date):
        """Get all events of isin_code since date"""

    def find_by_type_and_date(self, event_type: EventType, date: datetime.date):
        """Get the events of event_type in date"""

    def batch_save(self, records: List):
        """Saves a list of records"""
