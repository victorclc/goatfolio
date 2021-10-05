from dataclasses import dataclass


@dataclass
class NotifyRequest:
    level: str
    service: str
    message: str
