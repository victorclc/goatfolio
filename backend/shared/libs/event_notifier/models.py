from dataclasses import dataclass


@dataclass
class NotifyRequest:
    level: str
    service: str
    message: str


class NotifyLevel:
    INFO = "INFO"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
