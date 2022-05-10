from dataclasses import dataclass

from application.models.invesments import InvestmentType


@dataclass
class AddInvestmentRequest:
    type: InvestmentType
    investment: dict
    subject: str = ""

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = InvestmentType(self.type)

    def to_dict(self):
        return {**self.__dict__, "type": self.type.value}
