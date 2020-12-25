from dataclasses import dataclass


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
class Import:
    subject: str
    datetime: int
    username: str
    status: str
    result: str = None
