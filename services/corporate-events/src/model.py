from dataclasses import dataclass


@dataclass
class AsyncInvestmentAddRequest:
    subject: str
    type: InvestmentsType
    investment: dict
