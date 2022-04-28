import datetime
from dataclasses import dataclass
from typing import List

from application.investment import Investment


@dataclass
class PaginatedInvestmentsResult:
    investments: List[Investment]
    last_evaluated_id: str
    last_evaluated_date: datetime.date

    def to_dict(self):
        return {
            **self.__dict__,
            "investments": [i.to_json() for i in self.investments],
            "last_evaluated_date": self.last_evaluated_date.strftime("%Y%m%d")
        }
