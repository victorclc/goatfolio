from dataclasses import dataclass


@dataclass
class NotificationRequest:
    subject: str
    title: str
    message: str

