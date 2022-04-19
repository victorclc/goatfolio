from dataclasses import dataclass
from enum import Enum, auto


class NotificationTopic(Enum):
    DEFAULT = auto()
    COGNITO = auto()

    @classmethod
    def value_of(cls, value: str):
        for k, v in cls.__members__.items():
            if k == value.upper():
                return v
        else:
            raise ValueError(f"'{cls.__name__}' enum not found for '{value}'")


@dataclass
class NotifyRequest:
    level: str
    service: str
    message: str
    topic: NotificationTopic = NotificationTopic.DEFAULT

    def __post_init__(self):
        if isinstance(self.topic, str):
            self.topic = NotificationTopic.value_of(self.topic)
