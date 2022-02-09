from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    sub: str
    name: str
    email: str
