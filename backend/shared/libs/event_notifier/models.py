from dataclasses import dataclass
from enum import Enum, auto


class NotificationTopic(Enum):
    DEFAULT = auto()
    COGNITO = auto()


@dataclass
class NotifyRequest:
    level: str
    service: str
    message: str
    topic: NotificationTopic = NotificationTopic.DEFAULT

    def to_dict(self):
        return {**self.__dict__, "topic": self.topic.name}


class NotifyLevel:
    INFO = "INFO"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
