from dataclasses import dataclass


@dataclass
class NotificationRequest:
    subject: str
    title: str
    message: str


@dataclass
class NotificationMessageRequest:
    message_key: str
    title: str
    message: str
