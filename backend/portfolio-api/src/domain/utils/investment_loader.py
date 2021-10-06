from uuid import uuid4

from domain.enums.investment_type import InvestmentType
from domain.models.investment import (
    StockInvestment,
    Investment,
)


class MissingRequiredFields(Exception):
    def __init__(self, field, msg):
        self.field = field
        super().__init__(msg)


def load_model_by_type(
    _type: InvestmentType, investment: dict, generate_id: bool = True
) -> Investment:
    investment.pop("type", None)
    if "id" not in investment:
        if not generate_id:
            raise MissingRequiredFields("id", "Missing id field")
        investment["id"] = str(uuid4())
    if _type == InvestmentType.STOCK:
        return StockInvestment(**investment, type=InvestmentType.STOCK)
    raise TypeError
