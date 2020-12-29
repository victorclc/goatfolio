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

    def __post_init__(self):
        if isinstance(self.credentials, dict):
            self.credentials = CEICredentials(**self.credentials)


@dataclass
class CEICrawResult:
    subject: str
    datetime: int
    status: str = None
    payload: str = None
