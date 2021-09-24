from dataclasses import dataclass
from decimal import Decimal


@dataclass
class IntradayInfo:
    company_name: str
    current_price: Decimal
    yesterday_price: Decimal
    today_variation_percentage: Decimal
