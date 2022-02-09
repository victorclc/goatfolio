from dataclasses import dataclass, field
from datetime import datetime
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


@dataclass
class FriendRequest:
    from_: User
    to: User


@dataclass
class FriendsList:
    subject: str
    friends: List[Friend] = field(default_factory=list)
    requests: List[Friend] = field(default_factory=list)
    invites: List[Friend] = field(default_factory=list)
