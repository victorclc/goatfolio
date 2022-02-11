from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional

from application.models.user import User


@dataclass
class Friend:
    user: User
    date: Optional[datetime.date]

    def __hash__(self):
        return self.user.__hash__()

    def __eq__(self, other):
        if isinstance(other, User):
            return self.user.__eq__(other)
        if isinstance(other, Friend):
            return self.user.__eq__(other.user)
        return False

    def to_dict(self):
        return {
            "user": asdict(self.user),
            "date": self.date.strftime("%Y%m%d")
        }


class RequestType(Enum):
    TO = "TO"
    FROM = "FROM"


@dataclass
class FriendRequest:
    from_: User
    to: User
    type_: RequestType

    def to_dict(self):
        return {
            "from": asdict(self.from_),
            "to": asdict(self.to),
            "type": self.type_.value
        }


@dataclass
class FriendsList:
    subject: str
    friends: List[Friend] = field(default_factory=list)
    requests: List[Friend] = field(default_factory=list)  # recebo
    invites: List[Friend] = field(default_factory=list)  # envio

    def __post_init__(self):
        if not all(isinstance(elem, Friend) for elem in self.friends):
            self.friends = [Friend(**f) for f in self.friends]
        if not all(isinstance(elem, Friend) for elem in self.requests):
            self.requests = [Friend(**f) for f in self.requests]
        if not all(isinstance(elem, Friend) for elem in self.invites):
            self.invites = [Friend(**f) for f in self.invites]

    def add_friend_request(self, user: User):
        if user not in self.requests:
            self.requests.append(Friend(user, datetime.now().date()))

    def add_friend_invite(self, user: User):
        if user not in self.invites:
            self.requests.append(Friend(user, datetime.now().date()))

    def to_dict(self):
        return {
            **self.__dict__,
            "friends": [f.to_dict() for f in self.friends],
            "requests": [f.to_dict() for f in self.requests],
            "invites": [f.to_dict() for f in self.invites],
        }
