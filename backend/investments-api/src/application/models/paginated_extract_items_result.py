import datetime
from dataclasses import dataclass
from typing import List

from application.investment import Investment
from application.models.extract_item import ExtractItem


@dataclass
class PaginatedExtractItemsResult:
    items: List[ExtractItem]
    last_evaluated_id: str
    last_evaluated_date: datetime.date

    def to_dict(self):
        return {
            **self.__dict__,
            "items": [i.to_json() for i in self.items],
            "last_evaluated_date": self.last_evaluated_date.strftime("%Y%m%d") if self.last_evaluated_date else None
        }
