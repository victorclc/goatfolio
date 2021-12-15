import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class CompanyDetails:
    company_name: str
    trading_name: str
    ticker_code: str
    segment: str
    code_cvm: str
    url: str


@dataclass
class CompaniesUpdates:
    date: datetime.date
    companies: List[CompanyDetails]
