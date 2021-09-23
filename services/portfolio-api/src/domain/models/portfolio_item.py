from abc import ABC
from dataclasses import dataclass


@dataclass
class PortfolioItem(ABC):
    subject: str
    ticker: str
