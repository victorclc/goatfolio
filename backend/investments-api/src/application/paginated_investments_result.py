from dataclasses import dataclass
from typing import List

from application.investment import Investment


@dataclass
class PaginatedInvestmentsResult:
    investments: List[Investment]
    last_evaluated_id: str

    def to_dict(self):
        return {
            **self.__dict__,
            "investments": [i.to_json() for i in self.investments]
        }
