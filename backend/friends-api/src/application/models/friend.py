from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional

from application.models.user import User


@dataclass
class Friend:
    user: User
    date: Optional[datetime.date] = field(default_factory=lambda: datetime.now().date())

    def __hash__(self):
        return self.user.__hash__()

    def __eq__(self, other):
        if isinstance(other, User):
            return self.user.__eq__(other)
        if isinstance(other, Friend):
            return self.user.__eq__(other.user)
        return False

    def __post_init__(self):
        if isinstance(self.user, dict):
            self.user = User(**self.user)
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y%m%d")

    def to_dict(self):
        return {
            "user": asdict(self.user),
            "date": self.date.strftime("%Y%m%d")
        }


class RequestType(Enum):
    DECLINE_TO = "DECLINE_TO"
    DECLINE_FROM = "DECLINE_FROM"
    CANCEL_TO = "CANCEL_TO"
    CANCEL_FROM = "CANCEL_FROM"
    ACCEPT_TO = "ACCEPT_TO"
    ACCEPT_FROM = "ACCEPT_FROM"
    TO = "TO"
    FROM = "FROM"


@dataclass
class FriendRequest:
    from_: User
    to: User
    type_: RequestType

    def __post_init__(self):
        if isinstance(self.from_, dict):
            self.from_ = User(**self.from_)
        if isinstance(self.to, dict):
            self.to = User(**self.to)
        if isinstance(self.type_, str):
            self.type_ = RequestType(self.type_)

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

    def accept_request(self, user: User):
        self.requests.remove(user)
        self.add_friend(user)

    def invite_accepted(self, user: User):
        self.invites.remove(user)
        self.add_friend(user)

    def add_friend(self, user: User):
        if user not in self.friends:
            self.friends.append(Friend(user))

    def add_friend_request(self, user: User):
        if user not in self.requests:
            self.requests.append(Friend(user))

    def add_friend_invite(self, user: User):
        if user not in self.invites:
            self.invites.append(Friend(user))

    def user_exists_on_list(self, user: User) -> bool:
        return user in self.friends or user in self.requests or user in self.invites

    def user_exists_on_invites(self, user: User):
        return user in self.invites

    def user_exists_on_requests(self, user: User):
        return user in self.requests

    def user_exists_on_friends(self, user: User):
        return user in self.friends

    def to_dict(self):
        return {
            **self.__dict__,
            "friends": [f.to_dict() for f in self.friends],
            "requests": [f.to_dict() for f in self.requests],
            "invites": [f.to_dict() for f in self.invites],
        }
