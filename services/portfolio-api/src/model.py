from dataclasses import dataclass


@dataclass
class InvestmentRequest:
    type: str
    investment: dict
