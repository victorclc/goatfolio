from domain.enums.investment_type import InvestmentType
from domain.models.investment import (
    StockInvestment,
    PreFixedInvestment,
    PostFixedInvestment,
    CheckingAccountInvestment, Investment,
)


def load_model_by_type(_type, investment) -> Investment:
    investment.pop("type", None)
    if _type == InvestmentType.STOCK:
        return StockInvestment(**investment, type=InvestmentType.STOCK)
    if _type == InvestmentType.PRE_FIXED:
        return PreFixedInvestment(**investment, type=InvestmentType.PRE_FIXED)
    if _type == InvestmentType.POST_FIXED:
        return PostFixedInvestment(**investment, type=InvestmentType.POST_FIXED)
    if _type == InvestmentType.CHECKING_ACCOUNT:
        return CheckingAccountInvestment(
            **investment, type=InvestmentType.CHECKING_ACCOUNT
        )
    raise TypeError
