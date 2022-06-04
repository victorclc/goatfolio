from uuid import uuid4

from domain.common.investments import Investment, InvestmentType, StockInvestment, StockDividend


class MissingRequiredFields(Exception):
    def __init__(self, field, msg):
        self.field = field
        super().__init__(msg)


def load_model_by_type(
    _type: InvestmentType, investment: dict, generate_id: bool = True
) -> Investment:
    investment.pop("type", None)
    if "id" not in investment and not generate_id:
        raise MissingRequiredFields("id", "Missing id field")
    if _type == InvestmentType.STOCK:
        if "id" not in investment:
            investment["id"] = f"STOCK#{investment['ticker'].upper()}#{str(uuid4())}"
        return StockInvestment(**investment, type=InvestmentType.STOCK)
    if _type == InvestmentType.STOCK_DIVIDEND:
        if investment.get("id") is None:
            investment["id"] = f"STOCK_DIVIDEND#{investment['ticker'].upper()}#{str(uuid4())}"
        return StockDividend(**investment, type=InvestmentType.STOCK_DIVIDEND)
    raise TypeError
