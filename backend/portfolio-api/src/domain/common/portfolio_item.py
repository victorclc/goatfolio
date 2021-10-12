from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PortfolioItem(ABC):
    subject: str

    @property
    @abstractmethod
    def sk(self) -> str:
        """The sort key of the object"""

    def to_json(self):
        return {"subject": self.subject, "sk": self.sk}
