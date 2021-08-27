from dataclasses import dataclass

from goatcommons.constants import InvestmentsType


@dataclass
class CEIInboundRequest:
    tax_id: str
    password: str


@dataclass
class CEIOutboundRequest:
    subject: str
    datetime: int
    credentials: CEIInboundRequest


@dataclass
class CEIImportResult:
    subject: str
    datetime: int
    status: str
    payload: str
    login_error: bool = False


@dataclass
class Import:
    subject: str
    datetime: int
    status: str
    username: str = None
    payload: str = None
    error_message: str = None


@dataclass
class InvestmentRequest:
    type: InvestmentsType
    investment: dict


@dataclass
class CEIInfo:
    subject: str
    assets_quantities: dict
