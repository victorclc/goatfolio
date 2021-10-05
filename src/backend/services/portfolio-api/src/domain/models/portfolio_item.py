from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PortfolioItem(ABC):
    subject: str
    ticker: str

    @abstractmethod
    def to_dict(self):
        """Transform data to a dict"""
