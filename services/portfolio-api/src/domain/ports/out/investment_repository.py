from typing import Protocol, List

from goatcommons.models import Investment


class InvestmentRepository(Protocol):
    def find_by_subject(self, subject: str) -> List[Investment]:
        """Finds all Investments of given subject."""

    def save(self, investment: Investment):
        """Save an investment to the repository."""

    def delete(self, investment_id: str, subject: str):
        """Delete the Investment corresponding to the given investment_id of the repository"""

    def batch_save(self, investments: List[Investment]):
        """Save a list of investments into the repository."""
