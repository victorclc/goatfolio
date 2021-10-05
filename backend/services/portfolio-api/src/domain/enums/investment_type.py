from enum import Enum


class InvestmentType(Enum):
    STOCK = "STOCK"
    US_STOCK = "US_STOCK"
    FIXED_INCOME = "FIXED_INCOME"
    PRE_FIXED = "PRE_FIXED"
    POST_FIXED = "POST_FIXED"
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    CRYPTO = "CRYPTO"

    @classmethod
    def from_string(cls, _type: str):
        return cls(_type)
