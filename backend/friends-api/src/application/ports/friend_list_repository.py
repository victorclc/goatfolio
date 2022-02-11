import abc
from typing import Optional

from application.models.friend import FriendsList


class FriendsListRepository(abc.ABC):
    @abc.abstractmethod
    def find_by_subject(self, subject) -> Optional[FriendsList]:
        ...

    @abc.abstractmethod
    def save(self, friends_list: FriendsList):
        ...
