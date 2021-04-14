from dataclasses import dataclass


@dataclass
class CorporateEventData:
    company_name: str
    trading_name: str
    code: str
    segment: str
    code_cvm: str
    url: str
