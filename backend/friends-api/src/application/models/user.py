from dataclasses import dataclass


@dataclass
class User:
    sub: str
    name: str
    email: str
