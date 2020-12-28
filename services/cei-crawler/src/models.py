from dataclasses import dataclass


@dataclass
class CEICredentials:
    tax_id: str
    password: str


@dataclass
class CEICrawRequest:
    subject: str
    datetime: int
    credentials: CEICredentials


@dataclass
class CEICrawResult:
    subject: str
    datetime: int
    status: str = None
    payload: str = None
