from dataclasses import dataclass

from goatcommons.constants import InvestmentsType


@dataclass
class InvestmentRequest:
    type: InvestmentsType
    investment: dict
    subject: str = None
