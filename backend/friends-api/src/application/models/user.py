from dataclasses import dataclass


@dataclass(frozen=False)
class User:
    sub: str
    name: str
    email: str
