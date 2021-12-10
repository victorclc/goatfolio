from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from application.models.user import User


@dataclass
class Friend:
    name: str
    email: str
    sub: str
    date: Optional[datetime.date]


@dataclass
class FriendRequest:
    from_: User
    to: User


@dataclass
class FriendsList:
    friends: List[Friend]
    requests: List[Friend]
    pending: List[Friend]
