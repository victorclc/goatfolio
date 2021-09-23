from uuid import uuid4

from domain.enums.investment_type import InvestmentType
from domain.models.investment import (
    StockInvestment,
    Investment,
)


def load_model_by_type(_type: InvestmentType, investment: dict) -> Investment:
    investment.pop("type", None)
    if "id" not in investment:
        investment["id"] = str(uuid4())
    if _type == InvestmentType.STOCK:
        return StockInvestment(**investment, type=InvestmentType.STOCK)
    raise TypeError
