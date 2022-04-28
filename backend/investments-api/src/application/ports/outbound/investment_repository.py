import datetime
from typing import Protocol, List, Optional, Tuple

from application.investment import Investment


class InvestmentRepository(Protocol):
    def find_by_subject(
            self, subject: str,
            limit: Optional[int],
            last_evaluated_id: Optional[str],
            last_evaluated_date: Optional[datetime.date]
    ) -> Tuple[List[Investment], Optional[str], Optional[datetime.date]]:
        """Finds all Investments of given subject."""

    def save(self, investment: Investment):
        """Save an investment to the repository."""

    def delete(self, investment_id: str, subject: str):
        """Delete the Investment corresponding to the given investment_id of the repository"""

    def batch_save(self, investments: List[Investment]):
        """Save a list of investments into the repository."""
