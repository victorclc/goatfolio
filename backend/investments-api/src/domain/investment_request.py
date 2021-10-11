from dataclasses import dataclass

from domain.investment_type import InvestmentType


@dataclass
class InvestmentRequest:
    type: InvestmentType
    investment: dict
    subject: str = ""

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = InvestmentType(self.type)
